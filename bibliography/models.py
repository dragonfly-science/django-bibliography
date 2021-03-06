import os
import xml.etree.ElementTree as ET
import logging
import re  
import unicodedata

from subprocess import Popen, PIPE
from StringIO import StringIO

from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings

from taggit.managers import TaggableManager

from bibliography.utils import format_bytes


MODS_URI_DEFAULT = "http://www.loc.gov/mods/v3"
CSL_FILE_DEFAULT = os.path.join(os.path.dirname(__file__), 'apa.csl')

BIBLIOGRAPHY_MODS_URI = getattr(settings, 'BIBLIOGRAPHY_MODS_URI', MODS_URI_DEFAULT)
BIBLIOGRAPHY_CSL = getattr(settings, 'BIBLIOGRAPHY_CSL', CSL_FILE_DEFAULT)


class Reference(models.Model):
    key = models.SlugField(max_length=50, editable=False)

    bibtex = models.TextField()

    year = models.IntegerField(editable=False, null=True, blank=True)
    html = models.TextField(editable=False)
    sort = models.TextField(editable=False, null=True, blank=True)
    authors = models.TextField(null=True, blank=True)
    title = models.TextField(editable=False, null=True, blank=True)
    abstract = models.TextField(editable=False, null=True, blank=True)
    doi = models.TextField(editable=False, null=True, blank=True)
    tags = TaggableManager(blank=True)

    class Meta:
        unique_together = ("key",)
        ordering = ('sort', '-year', 'key')
    
    def __unicode__(self):
        return "%s:%s" % (self.key, self.id)

    def get_absolute_url(self):
        return "%s/references/%s.html"%(settings.SITE_URL, self.key)

    def the_tags(self):
        return ", ".join([t.name for t in self.tags.all()])
    the_tags.short_description = 'Tags'
    
    def save(self):
        if hasattr(self, '_tree'):  #Make sure cached copy of the xml tree is removed before parsing
            del self._tree
        self.key = self.get_key()
        self.year = self.get_year()
        self.html = self.get_html()
        self.sort = self.get_sort()
        self.authors = self.get_authors()
        self.title = self.get_title()
        self.abstract = self.get_abstract()
        self.doi = self.get_doi()
        try:
            existing = Reference.objects.get(key=self.key)
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
                abs_url = os.path.join(settings.MEDIA_ROOT, rel_url)
                f_type = re.sub('\.','',os.path.splitext(abs_url)[1])
                f_size = format_bytes(os.path.getsize(abs_url))
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
                abs_url = os.path.join(settings.MEDIA_ROOT, rel_url)
                f_type = re.sub('\.','',os.path.splitext(abs_url)[1])
                f_size = format_bytes(os.path.getsize(abs_url))
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
            for part in author.findall(".//{%s}%s"%(BIBLIOGRAPHY_MODS_URI, 'namePart')):
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

    def get_key(self):
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
    
    def get_html(self, csl=BIBLIOGRAPHY_CSL):
        bibtex = unicodedata.normalize('NFKD', unicode(self.bibtex)).encode('ascii','xmlcharrefreplace')
        bibtex = re.sub('\t','    ', bibtex)
        bibtex = re.sub('\n\s*\n', '<br><br>', bibtex)
        try:
            p = Popen(['bib2html', csl], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            html, err = p.communicate(bibtex)
            if p.returncode != 0:
                if settings.DEBUG:
                    logging.error("get_html stdout = %s" % html)
                    logging.error("get_html stderr = %s" % err)
                logging.warn("get_html return code = %s" % p.returncode)
                html = ''
        except OSError, e:
            html = ''
            logging.warn("Execution of bib2html failed: %s" % e)
        return html.decode('utf-8')

    def get_sort(self, csl=BIBLIOGRAPHY_CSL):
        try:
            p = Popen(['bib2sort', csl], stdin=PIPE, stdout=PIPE, stderr=PIPE)
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
        return self.get_xml_tree().find(".//{%s}%s" % (BIBLIOGRAPHY_MODS_URI, tag))

    def xml_findtext(self, tag):
        return self.get_xml_tree().findtext(".//{%s}%s" % (BIBLIOGRAPHY_MODS_URI, tag))

    def xml_findall(self, tag):
        return self.get_xml_tree().findall(".//{%s}%s" % (BIBLIOGRAPHY_MODS_URI, tag))

class Resource(models.Model):
    reference = models.ForeignKey('Reference')
    file = models.FileField(upload_to='resources', null=True, blank=True, max_length=256)
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255,null=True, blank=True)
    list_title = models.CharField(max_length=255, null=True, blank=True)
    pos = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.title, self.reference)
