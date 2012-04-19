# Script to get bibliography records from www.dragonfly.co.nz

import re
import sys
import os
import shutil
import optparse
from optparse import make_option
sys.path.append('/usr/local/django')

from django.core.management import setup_environ
from django.core.management.base import BaseCommand, CommandError

from bibliography.models import Reference

class ExportBibsCommand(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('-o', '--output', dest='output', help='Output file'), )
    option_list = BaseCommand.option_list + (make_option('-t', '--tags', dest='tags', action='append', help='Filter references with specified tags'), )
    self.can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings
        setup_environ(settings)

        refs = Reference.objects.all()
        if options.tags:
            for t in options.tags:
                refs = refs.filter(tags__name = t)

        bib = '\n\n'.join(r.bibtex for r in refs)

        with open(options.output or 'references.bib', 'w') as f:
            f.write(bib)
