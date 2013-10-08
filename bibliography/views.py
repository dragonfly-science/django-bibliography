from django.shortcuts import render_to_response, get_list_or_404
from django.template.loader import render_to_string
from django.template import RequestContext

from bibliography.models import Reference, Resource


def reference(request, key):
    current = None

    for r in get_list_or_404(Reference, key=key):
        current = r

    return render_to_response('references/view.html', {
        'current': current,
        'page': {'title': current.title },
        },
        RequestContext(request))


def tagging(request, tag_name):
    name = tag_name
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
    bib = Reference.objects.filter(key = key)[0].bibtex
    return render_to_response('references/bib.bib', dict(
                bib = bib), mimetype='text/plain')
