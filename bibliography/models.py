import os
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from StringIO import StringIO
import logging
import re  
from settings import MEDIA_ROOT
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from taggit.managers import TaggableManager
import unicodedata

try:
    from settings import BIBLIOGRAPHY_CSL
except ImportError:
    BIBLIOGRAPHY_CSL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apa.csl')
try:
    from settings import BIBLIOGRAPHY_MODS_URI
except ImportError:
    BIBLIOGRAPHY_MODS_URI = "http://www.loc.gov/mods/v3"

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%i TB' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%i GB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%i MB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%i kB' % kilobytes
    else:
        size = '%i bytes' % bytes
    return size

class Reference(models.Model):
    name = models.SlugField(max_length=50, editable=False)
    bibtex = models.TextField()
    year = models.IntegerField(editable=False, null=True, blank=True)
    html = models.TextField(editable=False)
    sort = models.TextField(editable=False, null=True, blank=True)
    authors = models.TextField(null=True, blank=True)
    title = models.TextField(editable=False, null=True, blank=True)
    abstract = models.TextField(editable=False, null=True, blank=True)
    doi = models.TextField(editable=False, null=True, blank=True)
    tags = TaggableManager()

    def __unicode__(self):
        return "%s:%s" % (self.name, self.id)

    class Meta:
        unique_together = ("name",)
        ordering = ('sort', '-year', 'name')
    
    def get_absolute_url(self):
        return "%s/references/%s.html"%(settings.SITE_URL, self.name)

    def the_tags(self):
        return ", ".join([t.name for t in self.tags.all()])
    the_tags.short_description = 'Tags'
    
    def save(self):
        if hasattr(self, '_tree'):  #Make sure cached copy of the xml tree is removed before parsing
            del self._tree
        self.name = self.get_name()
        self.year = self.get_year()
        self.html = self.get_html()
        self.sort = self.get_sort()
        self.authors = self.get_authors()
        self.title = self.get_title()
        self.abstract = self.get_abstract()
        self.doi = self.get_doi()
        try:
            existing = Reference.objects.get(name=self.name)
            self.id = existing.id
        except ObjectDoesNotExist:
            pass
        super(Reference, self).save()

    def gscholar(self):
        return "http://scholar.google.com/scholar?q=%s" % re.sub(' ','+',self.title)
    
    def google(self):
        return "http://www.google.com/search?hl=en&q=%s" % re.sub(' ','+',self.title)

    def set_keywords(self):
        s = re.search("(?<=keywords)(.*)", self.bibtex)
        if s:
            s = s.group(0)
            s = re.sub("^[ \t=]+","",s)
            s = re.sub("[ \t,]+$","",s)
            s = re.sub("[\"{}]","", s)
            ss = s.split(",")
            for s1 in ss:
                self.tags.add(s1.strip().lower())

    def file_list(self):
        allfiles =  self.resource_set.all()
        dic = []
        for f in allfiles:
            ffile = f.file
            if ffile:
                rel_url = ffile.url
                abs_url = os.path.join(MEDIA_ROOT, rel_url)
                f_type = re.sub('\.','',os.path.splitext(abs_url)[1])
                f_size = convert_bytes(os.path.getsize(abs_url))
                dic.append(dict(name=f.title, file=rel_url, type=f_type, size=f_size))
        return dic

    def url_list(self):
        allurls =  self.resource_set.all()
        dic = []
        for u in allurls:
            uurl = u.url
            if uurl:
                dic.append(dict(name=u.title, url=uurl))
        return dic

    def res_list(self):
        allres = self.resource_set.all()
        dic = []
        for r in allres:
            if r.file:
                rel_url = r.file.url
                abs_url = os.path.join(MEDIA_ROOT, rel_url)
                f_type = re.sub('\.','',os.path.splitext(abs_url)[1])
                f_size = convert_bytes(os.path.getsize(abs_url))
                dic.append(dict(name=r.title, short_name=r.list_title, file=rel_url, type=f_type, size=f_size, url=None, pos=r.pos))
            elif r.url:
                dic.append(dict(name=r.title, short_name=r.list_title, file=None, type=None, size=None, url=r.url, pos=r.pos))
        return sorted(dic, key=lambda a: a['pos'])
    
    def with_resources(self):
        res = False
        if self.resource_set.count():
            res = True
        return res
    with_resources.boolean = True
    with_resources.short_description = 'Res.'

    ### Methods for getting attributes from the bibtex record
    def get_abstract(self):
        return self.xml_findtext('abstract')
    
    def get_authors(self):
        fullnames = []
        for author in self.xml_findall('name'):
            fullname = []
            for part in author.findall(".//{%s}%s"%(MODS_URI, 'namePart')):
                fullname.append(part.text)
            fullnames.append(' '.join(fullname))
        if len(fullnames)>1:
            s2 = ''.join([fullnames[i] + ', ' for i in xrange(len(fullnames)-2)])
            s3 = s2 + fullnames[-2] + ' & ' + fullnames[-1]
        else:
            s3 = ''.join(fullnames)
        return s3

    def get_doi(self):
        doi = ''
        for identifier in self.xml_findall('identifier'):
            if identifier.get('type') == 'doi':
                doi = identifier.text
        return doi

    def get_title(self):          
        return self.xml_findtext('title')

    def get_name(self):
        return self.xml_find('mods').get('ID')
    
    def get_year(self): 
        year = self.xml_findtext('date') or self.xml_findtext('dateIssued')
        if year:
            try:
                year = int(year)
            except:
                raise ValidationError('Cannot parse year from date field: %s' % self.year)
            return year

    def get_xml(self):
        bibtex = unicodedata.normalize('NFKD', unicode(self.bibtex)).encode('ascii','xmlcharrefreplace')
        bibtex = re.sub('\t','    ', bibtex)
        bibtex = re.sub('\n\s*\n', '<br><br>', bibtex)
        bibtex = re.sub('\r\n\s*\r\n', '<br><br>', bibtex)
        xml = ''
        try:
            p = Popen('bib2xml', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            xml, err = p.communicate(bibtex)
            if p.returncode != 0:
                raise ValidationError('Non zero return code from bib2xml: %s ' %  p.returncode)
        except OSError, e:
            logging.warn("Execution of bib2xml failed: %s" % e)
            raise ValidationError('Error parsing xml: %s ' % e)
        return xml
    
    def get_html(self):
        bibtex = unicodedata.normalize('NFKD', unicode(self.bibtex)).encode('ascii','xmlcharrefreplace')
        bibtex = re.sub('\t','    ', bibtex)
        bibtex = re.sub('\n\s*\n', '<br><br>', bibtex)
        try:
            p = Popen(['bib2html', BIBLIOGRAPHY_CSL], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            html, err = p.communicate(bibtex)
            if p.returncode != 0:
                logging.warn("get_html return code = %s" % p.returncode)
                html = ''
        except OSError, e:
            html = ''
            logging.warn("Execution of bib2html failed: %s" % e)
        return html

    def get_sort(self):
        try:
            p = Popen(['bib2sort', BIBLIOGRAPHY_CSL], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            sort, err = p.communicate(self.bibtex)
            if p.returncode != 0:
                logging.warn("get_sort return code = %s" % p.returncode)
                sort = ''
        except OSError, e:
            sort = ''
            logging.warn("Execution of bib2sort failed: %s" % e)
        return sort

    ### XML parsing methods ...
    def get_xml_tree(self):
        if not hasattr(self, '_tree'):
            self._tree = ET.parse(StringIO(self.get_xml())) # Cache a copy of the xml tree to cut down calls to shell
        return self._tree
    
    def xml_find(self, tag):
        return self.get_xml_tree().find(".//{%s}%s"%(MODS_URI, tag))

    def xml_findtext(self, tag):
        return self.get_xml_tree().findtext(".//{%s}%s"%(MODS_URI, tag))

    def xml_findall(self, tag):
        return self.get_xml_tree().findall(".//{%s}%s"%(MODS_URI, tag))

class Resource(models.Model):
    reference = models.ForeignKey('Reference')
    file = models.FileField(upload_to='resources', null=True, blank=True, max_length=256)
    url = models.URLField(verify_exists=False, null=True, blank=True)
    title = models.CharField(max_length=255,null=True, blank=True)
    list_title = models.CharField(max_length=255, null=True, blank=True)
    pos = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return "%s - %s" % (self.title, self.reference)
