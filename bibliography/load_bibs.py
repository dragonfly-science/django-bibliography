# Script to load bibliography records from file
# Overwrites existing records with the same name

import sys
import os
import shutil
import optparse
import pdb
sys.path.append('/usr/local/django')

from django.core.management import setup_environ
from www import settings

setup_environ(settings)

import re
from www.bibliography.models import Reference

usage = "usage: %prog [-i -t -f]"
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--import', dest='in_file', default='publications-import.bib', help='Bib file to import')
parser.add_option('-t', '--tags', action='append', default=[], dest='tags', help='Tag to be added to all imported references')
parser.add_option('-f', '--force', dest='force', action='store_true', default=False, help='Force import')
parser.add_option('-c', '--clean', dest='clear', action='store_true', default=False, help='Clear tags before update')
options, remainder=parser.parse_args()

file = options.in_file

print '-- Importing references in %s' % options.in_file

if not os.path.exists(options.in_file):
    parser.error('Input file does not exist.')

if options.force:
    print '-- Force import'

if options.clear:
    print '-- Clear tags before import'

#file = 'bibliography/publications-import.bib'
f = open(file, 'r')
contents = f.read().decode('utf-8')
f.close()

def get_keywords(txt):
    s = re.search("keywords\s*=\s*\"(.*?)\"\s*[,]*\s*\n", txt, re.DOTALL)
    if s:
        s = s.group(1)
        s = re.sub('[\n\{\}]+', '', s)
        s = s.split(',')
        return [si.lower().strip() for si in s]

cont =  contents.split("@")
cont.pop(0)

def get_key(txt):
    a = re.search('{\s*([\w-]+)\s*,',txt)
    if a:
        return(a.group(1))

def get_relfile(txt):
    a = re.findall('file.*\"(.*)\"',txt)
    if a:
        a = a[0]
        return [s.strip() for s in a.split(',')]

allkeys = [x.key for x in Reference.objects.all()]

nsuccess = 0
nfail = 0
nfiles = 0

for rec in cont:
    rkey = get_key(rec)
    ref = Reference.objects.filter(key = rkey)
    if ref:
        bib = Reference.objects.get(key = rkey)
        bib.bibtex = '@%s' % rec
        action = 'Updating'
    else:
        bib = Reference(bibtex = '@%s'% rec)
        action = 'Creating'
    #pdb.set_trace()
    try: 
        bib.clean()
    except:
        pdb.set_trace()
        print "Warning: Failed to load @%s" % rec
        nfail += 1
        continue
    if not rkey in allkeys or options.force:
        print "%s %s" % (action, rkey)
        bib.save()
        if options.clear:
            bib.tags.clear()
        for a in options.tags:
                    bib.tags.add(a)
        keywords = get_keywords(rec)
        if keywords:
            for k in keywords:
                bib.tags.add(k)
        if os.path.exists('files/%s' % rkey):
            files = os.listdir('files/%s' % rkey)
            for f in files:
                shutil.copy('files/%s/%s' % (rkey, f), '%s/resources/%s' % (settings.MEDIA_ROOT, f))
                res = bib.resource_set.create(file='resources/%s' % f, title='%s' % f)
                print 'Found and added %s' % f
                nfiles += 1
        bib.save()
        nsuccess += 1    
        allkeys.append(rkey.decode())

    else:
        print "Skipped pre-existing key: %s" % rkey
        nfail += 1

print "\n=> Imported %i references and %i files. %i failed." % (nsuccess, nfiles, nfail)




