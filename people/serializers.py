"""
Serialize models to and deserialize from JSON.
"""

from rest_framework import serializers

from . import models


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'pk',
            'name',
        ]


class MinimalPersonSerializer(serializers.ModelSerializer):
    """
    Serializer containing just the necessary fields to identify a :class:`Person`.

    Used for nesting within other serializers.
    """
    class Meta:
        model = models.Person
        fields = [
            'pk',
            'name',
        ]

        
class RelationshipSerializer(serializers.ModelSerializer):
    source = MinimalPersonSerializer()
    target = MinimalPersonSerializer()

    class Meta:
        model = models.Relationship
        fields = [
            'pk',
            'source',
            'target',
        ]
