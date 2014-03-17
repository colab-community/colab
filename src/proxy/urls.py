
from django.conf.urls import patterns, include, url

from .views import TracProxyView, JenkinsProxyView, GitlabProxyView


urlpatterns = patterns('',
    # Trac URLs
    url(r'^(?P<path>(?:admin|wiki|changeset|newticket|ticket|chrome|timeline|roadmap|browser|report|tags|query|about|prefs|log|attachment|raw-attachment|diff|milestone).*)$',
        TracProxyView.as_view()),

    # Jenkins URLs
    url(r'^ci/(?P<path>.*)$', JenkinsProxyView.as_view()),

    # Gitlab URLs

    url(r'^gitlab/(?P<path>.*)$',
        GitlabProxyView.as_view()),

    url(r'^(?P<path>(?:users|dashboard).*)$',
        GitlabProxyView.as_view()),
)