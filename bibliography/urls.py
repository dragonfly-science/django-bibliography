import os

from django.conf.urls.defaults import patterns
from django.conf import settings

from bibliography.views import get_bib, reference, tagging


urlpatterns = patterns('',
    (r'references/(?P<key>[a-zA-Z0-9_\-]+)\.bib$', get_bib),
    (r'references/(?P<key>[a-zA-Z0-9_\-]+)\.html$', reference),

    (r'^resources/(?P<path>.*)$',   'django.views.static.serve', {
        'document_root': os.path.join(settings.MEDIA_ROOT, 'resources')
        }),

    (r'^admin/tagging/(.*)$', tagging),
)
