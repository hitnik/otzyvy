from rest_framework import serializers
from .models import *
from rest_framework.reverse import reverse
import urllib

# Sites model serializer
class SitesModelSerializer(serializers.ModelSerializer):
    forums = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Sites
        fields = ['id', 'name', 'short', 'count', 'forums']

    def get_forums(self, obj):
        return '{}?{}'.format(
            reverse('forumTopics:forums-list', kwargs={}, request=self.context['request']),
            urllib.parse.urlencode({'site': obj.id})
        )

    def get_count(self, obj):
        request = self.context['request']
        date = request.GET.get('date','')
        if date:
            return '{}?{}'.format(
                reverse('forumTopics:topics_count', kwargs={'pk': obj.id}, request=request),
                urllib.parse.urlencode({'date':date})
                )
        return reverse('forumTopics:topics_count', kwargs={'pk': obj.id}, request=request)



class TopicsCountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()

class DateSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['iso-8601'])


class TopicsModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topics
        fields = ['id', 'user', 'topicText', 'site', 'datePost', 'url']


class ForumsModelSerializer(serializers.HyperlinkedModelSerializer):
    site = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Forums
        fields = ['id', 'name', 'site',]


class ForumUsersModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ForumUsers
        fields = '__all__'

class TopicsModelSerializer(serializers.ModelSerializer):
    user = ForumUsersModelSerializer(read_only=True)

    class Meta:
        model = Topics
        fields = ('id', 'user', 'topicText', 'datePost', 'url')