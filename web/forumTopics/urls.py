from django.conf.urls import url
from django.urls import path, include
from . import views
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

app_name = 'forumTopics'

router = DefaultRouter()
router.register(r'sites', views.SitesReadOnlyViewSet, basename='sites'),
router.register(r'forums', views.ForumsReadOnlyViewSet, basename='forums')
router.register(r'topics', views.TopicsReadOnlyViewSet, basename='topics')

urlpatterns = [
    url(r'^$', cache_page(600)(views.forums), name='forums'),
    url(r'^(?P<siteId>[0-9]+)$', views.forums),
    url(r'^(?P<siteId>[0-9]+)/$', views.forums),
    url(r'^(?P<siteId>[0-9]+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', views.forums),
    url(r'^topics/$', views.forumTopics, name='ForumTopics'),
    path('pdf', views.pdf_as_response, name='forums_pdf'),
    path('v1/topics-count/<int:pk>', views.TopicsCount.as_view(), name='topics_count'),
    path('v1/', include(router.urls)),
    path('jobs', views.ScheduledJobsView.as_view(), name='jobs'),
]
