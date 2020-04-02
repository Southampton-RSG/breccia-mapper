from rest_framework import serializers

from activities import models

from . import base
from . import people as people_serializers


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActivityType
        fields = [
            'pk',
            'name',
        ]


class ActivityMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActivityMedium
        fields = [
            'pk',
            'name',
        ]


class ActivitySeriesSerializer(serializers.ModelSerializer):
    type = ActivityTypeSerializer()
    medium = ActivityMediumSerializer()
    
    class Meta:
        model = models.ActivitySeries
        fields = [
            'pk',
            'name',
            'type',
            'medium',
        ]


class ActivitySerializer(base.FlattenedModelSerializer):
    series = ActivitySeriesSerializer()
    type = ActivityTypeSerializer()
    medium = ActivityMediumSerializer()

    class Meta:
        model = models.Activity
        fields = [
            'pk',
            'name',
            'series',
            'type',
            'medium',
        ]
        
        
class SimpleActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields = [
            'pk',
            'name',
        ]


class ActivityAttendanceSerializer(base.FlattenedModelSerializer):
    activity = SimpleActivitySerializer()
    person = people_serializers.SimplePersonSerializer()
    
    class Meta:
        model = models.Activity.attendance_list.through
        fields = [
            'pk',
            'activity',
            'person',
        ]
