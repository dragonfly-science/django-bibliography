# Script to get bibliography records from www.dragonfly.co.nz

import sys
import os
import shutil
import optparse
sys.path.append('/usr/local/django')

from django.core.management import setup_environ
from www import settings

setup_environ(settings)

import re
from www.bibliography.models import Reference

parser = optparse.OptionParser()
parser.add_option('-o', '--output', dest='output', help='Output file')
parser.add_option('-t', '--tags', dest='tags', action='append', help='Filter references with specified tags')
options, remainder=parser.parse_args()

refs = Reference.objects.all()
if options.tags:
    for t in options.tags:
        refs = refs.filter(tags__name = t)

bibs = []
for r in refs:
    bibs.append(r.bibtex)
bib = '\n\n'.join(bibs)

if options.output:
    f = open(options.output, 'w')
else:
    f = open('references.bib', 'w')
f.write(bib)
f.close()



