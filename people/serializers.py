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
        
        
class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Relationship
        fields = [
            'pk',
            'source',
            'target',
        ]
