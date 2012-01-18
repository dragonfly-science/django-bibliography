import re
import logging

from django.shortcuts import render_to_response, get_list_or_404
from django.template.loader import render_to_string
from django.template import RequestContext

from bibliography.models import *

def markdown_post_references(text, instance=None, check=False):
    def insert_references(m):
        try:
            return listview(None, query=m.group(1))
        except:
            if check: raise 
            return ""
    text = re.sub('\[References\s*(\w[\w=\'" -]+)\]', insert_references,  text)
    return text

def listview(request, query):
    tags = re.findall('tag=([\w-]+)', query)
    year = re.findall('year=([\d]+)', query)
    order = re.findall('order=([\w-]+)', query)
    key = re.findall('key=([\w-]+)', query)
    try:
        year = int(year[0])
    except:
        year = None
    references = Reference.objects.all() 
    if tags:
        for t in tags:
            references = references.filter(tags__name=t)
    if year:
        references = references.filter(year=year)
    if key:
        references = references.filter(name__in=key)
    references = references.distinct()
    if order:
        references = references.order_by(*order)
    else:
        references = references.order_by('sort', '-year') 
    if request:
        return render_to_string('references/list.html', dict(
                references = references
            ), RequestContext(request))
    else:
        return render_to_string('references/list.html', dict(
                references = references
            ))

def tagging(request,  name):
    if name:
        t = name.split('|')
        t = [ti.strip() for ti in t]
        references = Reference.objects.all()
        for ti in t:
            references = references.filter(tags__name = ti)
    else:
        references = Reference.objects.all()
    if request:
        return render_to_response('references/tagging.html', dict(
                references = references
            ), RequestContext(request))
    else:
        return render_to_string('references/tagging.html', dict(
                references = references
            ))

def get_bib(request, key):
    bib = Reference.objects.filter(name = key)[0].bibtex
    return render_to_response('references/bib.bib', dict(
                bib = bib), mimetype='text/plain')

