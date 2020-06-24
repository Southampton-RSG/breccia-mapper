import typing

from rest_framework import serializers

from people import models

from . import base


class SimplePersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'id',
            'name',
        ]


class PersonSerializer(base.FlattenedModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'id',
            'name',
            'gender',
            'age_group',
            'nationality',
            'country_of_residence',
            'organisation',
            'organisation_started_date',
        ]


class RelationshipSerializer(base.FlattenedModelSerializer):
    source = SimplePersonSerializer()
    target = SimplePersonSerializer()

    class Meta:
        model = models.Relationship
        fields = [
            'id',
            'source',
            'target',
        ]


class RelationshipAnswerSetSerializer(base.FlattenedModelSerializer):
    relationship = RelationshipSerializer()

    class Meta:
        model = models.RelationshipAnswerSet
        fields = [
            'id',
            'relationship',
            'timestamp',
            'replaced_timestamp',
        ]

    @property
    def column_headers(self) -> typing.List[str]:
        headers = super().column_headers

        # Add relationship questions to columns
        for question in models.RelationshipQuestion.objects.all():
            headers.append(question.slug.replace('-', '_'))

        return headers

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        try:
            # Add relationship question answers to data
            for answer in instance.question_answers.all():
                rep[answer.question.slug.replace('-',
                                                 '_')] = answer.slug.replace(
                                                     '-', '_')

        except AttributeError:
            pass

        return rep
