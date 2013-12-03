import os

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings

from bibliography.views import get_bib, reference, tagging


urlpatterns = patterns('',
    url(r'references/(?P<key>[a-zA-Z0-9_\-]+)\.bib$', get_bib, name='show_reference_as_bibtex'),
    url(r'references/(?P<key>[a-zA-Z0-9_\-]+)\.html$', reference, name='show_reference'),

    url(r'^resources/(?P<path>.*)$',   'django.views.static.serve', {
        'document_root': os.path.join(settings.MEDIA_ROOT, 'resources')
        }, name='serve_resource'),

    url(r'^admin/tagging/(?P<tag_name>.*)$', tagging, name='admin_tagging'),
)
 
if getattr(settings, 'BIBLIOGRAPHY_DEV_MODE', False):
    # Only load in admin if we are doing local work on django-bibliography
    admin.autodiscover()

    urlpatterns += patterns('',
        (r'^admin/', include(admin.site.urls)),
    )
