import re

from django.template.loader import render_to_string
from django.template import RequestContext


def format_bytes(num_bytes):
    """
    >>> format_bytes(10)
    '10 bytes'
    >>> format_bytes(100000)
    '97 kB'
    >>> format_bytes(100000000)
    '95 MB'
    >>> format_bytes(100000000000)
    '93 GB'
    >>> format_bytes(10000000000000)
    '9 TB'
    """
    num_bytes = float(num_bytes)
    if num_bytes >= 1099511627776:
        terabytes = num_bytes / 1099511627776
        size = '%i TB' % terabytes
    elif num_bytes >= 1073741824:
        gigabytes = num_bytes / 1073741824
        size = '%i GB' % gigabytes
    elif num_bytes >= 1048576:
        megabytes = num_bytes / 1048576
        size = '%i MB' % megabytes
    elif num_bytes >= 1024:
        kilobytes = num_bytes / 1024
        size = '%i kB' % kilobytes
    else:
        size = '%i bytes' % num_bytes
    return size


def listview(request, query):
    """ Turn a [Reference] query into a list of properly formatted references """
    from bibliography.models import Reference
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
        references = references.filter(key__in=key)
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


def markdown_post_references(text, check=False):
    """
    Process markdown text and replace occurrences of [References] tag
    with citations.
    """
    def insert_references(m):
        try:
            return listview(None, query=m.group(1))
        except:
            if check:
                raise 
            return ""

    return re.sub('\[References\s*(\w[\w=\'" -]+)\]', insert_references,  text)
