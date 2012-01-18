from django.conf.urls.defaults import *

from www.bibliography.views import *

urlpatterns = patterns('',
    (r'^(?P<key>[a-zA-Z0-9_\-]+)\.bib$', get_bib),
    (r'^(?P<key>[a-zA-Z0-9_\-]+)\.html$',   view),
)


