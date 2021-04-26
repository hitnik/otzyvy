from django.shortcuts import render
from .models import Sites, Forums, Topics
import datetime
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseNotFound
from django.conf import settings
from django.http import HttpResponseBadRequest ,HttpResponse
import pytz
import requests
from .utils import generate_forums_pdf_template_as_string
from rest_framework import viewsets, generics, views, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from .serializers import *
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import django_rq
from django.conf import settings

def forums(request, **kwargs ):

    today = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    local_tz = pytz.timezone(settings.TIME_ZONE)
    today = today.astimezone(local_tz).date()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    date = yesterday
    if 'siteId' in kwargs:
           siteId=kwargs['siteId']
    else: siteId=1
    if Sites.objects.filter(id=int(siteId)).exists():
        siteList = Sites.objects.filter(isActive=True).order_by('id')
        if 'year' in kwargs and 'month' in kwargs and 'day' in kwargs:
            dateString=kwargs['day']+'.'+kwargs['month']+'.'+kwargs['year']
            try:
                date = datetime.datetime.strptime(dateString, '%d.%m.%Y')
                date = datetime.date(date.year, date.month, date.day)
                yearAgo = today
                yearAgo = yearAgo-datetime.timedelta(days=365)
                if date < yearAgo or date > today:
                    raise ValueError
            except ValueError:
                if request.is_ajax():
                    response = JsonResponse()
                    response.status_code = 400
                    return response
                else:
                   return HttpResponseNotFound('<h1 style="text-align:center">Страница не найдена, '
                                                'попробуйте изменить условия поиска</h1>')
        siteDict = {}
        for site in siteList:
            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
                count = Topics.objects.filter(site__site_id=site.id,
                                          datePost__mysql_datetz=date, site__isActive=True).count()
            else:
                count = Topics.objects.filter(site__site_id=site.id,
                                          datePost__date=date, site__isActive=True).count()

            siteDict[site] = count

        forumsList = Forums.objects.filter(site_id=int(siteId),isActive=True).order_by('id')
        topicDict = getTopicsDict(forumsList,date)

        if request.is_ajax():
            return JsonResponse({"result":"ok"})
        return render(request, 'forumTopics/index.html', {'siteDict': siteDict,
                                                          'dateString': date.strftime('%d.%m.%Y'),
                                                          'topicDict': topicDict, 'siteId': int(siteId)})
    else:
        return HttpResponseNotFound('<h1 style="text-align:center">Страница не найдена, '
                                    'попробуйте изменить условия поиска</h1>')


def forumTopics(request):

    if request.is_ajax():
        forumsList = Forums.objects.filter(site_id=request.GET['siteId'],isActive=True).order_by('id')
        date = datetime.datetime.strptime(request.GET['dateString'], '%d.%m.%Y')
        topicDict = getTopicsDict(forumsList,date)
        html = render_to_string('forumTopics/tabcontent.html', {'topicDict':topicDict})
        data = {'content':html}
        return JsonResponse(data)

def getTopicsDict(forumsList,date):
    topicDict = {}
    for forum in forumsList:
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
            topicsList = Topics.objects.filter(site_id=forum.id, datePost__mysql_datetz=date).order_by('datePost')
        else:
            topicsList = Topics.objects.filter(site_id=forum.id, datePost__date=date).order_by('datePost')
        
        topicDict[forum] = topicsList
    return topicDict


def pdf_as_response(request):

    html = generate_forums_pdf_template_as_string(request)
    pdf = requests.post(settings.PDF_GENERATOR_URL, data={'html': html})
    return HttpResponse(pdf.content, content_type='application/pdf')


class SitesReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sites.objects.all().filter(isActive=True)
    serializer_class = SitesModelSerializer


class TopicsCount(generics.RetrieveAPIView):
    serializer_class = TopicsCountSerializer
    queryset = Sites.objects.all()

    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        forums = Forums.objects.filter(site=self.object)
        topics = Topics.objects.filter(site__in=forums)
        serializer_date = DateSerializer(data={'date': request.GET.get('date')})
        if serializer_date.is_valid():
            date = serializer_date.validated_data['date']
            topics = topics.filter(datePost__month=date.month,
                                   datePost__year=date.year,
                                   datePost__day=date.day
                                   )
        data = {'id': self.object.id, 'count': topics.count()}
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class ForumsFilterSet(filters.FilterSet):
    site = filters.ModelChoiceFilter(queryset=Sites.objects.all())

    class Meta:
        model = Forums
        fields = ['site', ]


class ForumsReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Forums.objects.filter(isActive=True)
    serializer_class = ForumsModelSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = ForumsFilterSet
    ordering_fields = ['id']
    ordering = ['id']

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        topics = Topics.objects.all()
        serializer_date = DateSerializer(data={'date': request.GET.get('date')})
        forums_list = []
        for obj in queryset:
            serializer_forums = self.get_serializer(obj)
            topicsList = topics.filter(site=obj)
            if serializer_date.is_valid():
                if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
                    topicsList = topicsList.filter(datePost__mysql_datetz=serializer_date.validated_data['date'])
                else:
                    topicsList = topicsList.filter(datePost__date=serializer_date.validated_data['date'])

            dict = serializer_forums.data
            dict['count'] = topicsList.count()
            dict['topicsUrl'] = None
            if topicsList.count() > 0:
                url_params = {'site': obj.id}
                if request.GET.get('date'):
                    url_params['date'] = request.GET.get('date')
                dict['topicsUrl'] = '{}?{}'.format(
                    reverse('forumTopics:topics-list', kwargs={}, request=request),
                    urllib.parse.urlencode(url_params)
                        )
            forums_list.append(dict)

        return Response(forums_list)

class TopicFilterSet(filters.FilterSet):
    site = filters.ModelChoiceFilter(queryset=Forums.objects.all())

    class Meta:
        model = Topics
        fields = ('site',)

class TopicsPageNumberPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100
    page_size_query_param = 'page_size'

class TopicsReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topics.objects.all()
    serializer_class = TopicsModelSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = TopicFilterSet
    ordering_fields = ['datePost']
    ordering = ['datePost']
    pagination_class = TopicsPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer_date = DateSerializer(data={'date': request.GET.get('date')})
        if serializer_date.is_valid():
            date = serializer_date.validated_data['date']
            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
                queryset = queryset.filter(datePost__mysql_datetz=date)
            else:
                queryset = queryset.filter(datePost__date=date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ScheduledJobsView(APIView):
    def get(self, request, format=None):
        data = {}
        rq_queues = settings.RQ_QUEUES
        for queue, value in rq_queues.items():
            scheduler = django_rq.get_scheduler(queue)
            data[queue] = []
            for job in scheduler.get_jobs():
                job_data = {}
                job_data['id'] = job.get_id()
                job_data['func_name'] = job.func_name
                job_data['meta'] = job.meta
                job_data['result_ttl'] = job.result_ttl
                data[queue].append(job_data)

        return Response(data)