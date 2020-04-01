from rest_framework import serializers

from activities import models

from . import base


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
           'name',
           'series',
           'type',
           'medium',
        ]
