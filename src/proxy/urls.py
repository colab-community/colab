
from django.conf.urls import patterns, include, url

from .views import TracProxyView, JenkinsProxyView, GitlabProxyView, RedmineProxyView


urlpatterns = patterns('',
    # Trac URLs
    url(r'^(?P<path>(?:admin|wiki|changeset|newticket|ticket|chrome|timeline|roadmap|browser|report|tags|query|about|prefs|log|attachment|raw-attachment|diff|milestone).*)$',
        TracProxyView.as_view()),

    # Jenkins URLs
    url(r'^ci/(?P<path>.*)$', JenkinsProxyView.as_view()),

    # Gitlab URLs
    url(r'^(?P<path>(?:users|dashboard|profile).*)$',
        GitlabProxyView.as_view()),

    #  URLs
    url(r'^(?P<path>(?:projects).*)$',
        RedmineProxyView.as_view()),
)
