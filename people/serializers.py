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


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organisation
        fields = [
            'pk',
            'name',
        ]


class RelationshipSerializer(serializers.ModelSerializer):
    source = PersonSerializer()
    target = PersonSerializer()

    class Meta:
        model = models.Relationship
        fields = [
            'pk',
            'source',
            'target',
        ]


class OrganisationRelationshipSerializer(serializers.ModelSerializer):
    source = PersonSerializer()
    target = OrganisationSerializer()

    class Meta:
        model = models.OrganisationRelationship
        fields = [
            'pk',
            'source',
            'target',
        ]
