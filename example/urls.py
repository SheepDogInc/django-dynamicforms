from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'survey.views.home'),
    url(r'^poll/(?P<poll_id>[0-9]+)$', 'survey.views.poll', name='poll'),
)
