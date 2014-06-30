
from django.conf.urls import patterns, include, url

from .views import ProxyView, TracProxyView, JenkinsProxyView, GitlabProxyView, RedmineProxyView

urlpatterns = patterns('',
    # Trac URLs
    url(r'^(?P<path>(?:admin|wiki|changeset|newticket|ticket|chrome|timeline|roadmap|browser|report|tags|query|about|prefs|log|attachment|raw-attachment|diff|milestone).*)$',
        TracProxyView.as_view()),

    # Trac extra URLs
    url(r'^trac/(?P<path>.*)$', TracProxyView.as_view()),

    # Jenkins URLs
    url(r'^ci/(?P<path>.*)$', JenkinsProxyView.as_view()),

    # Gitlab extra URLs
    url(r'^gitlab/(?P<path>.*)$', GitlabProxyView.as_view()),

    # Redmine
    url(r'^redmine/(?P<path>.*)$', RedmineProxyView.as_view()),
)
