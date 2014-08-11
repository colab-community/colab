
from django.conf.urls import patterns, include, url

from .views import ProxyView, GitlabProxyView, RedmineProxyView


urlpatterns = patterns('',
    # Gitlab extra URLs
    url(r'^gitlab/(?P<path>.*)$', GitlabProxyView.as_view()),

    # Redmine
    url(r'^redmine/(?P<path>.*)$', RedmineProxyView.as_view()),
)
