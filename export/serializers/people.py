import typing

from rest_framework import serializers

from people import models

from . import base


class PersonSerializer(base.FlattenedModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'id',
            # Name is excluded from exports
            # See https://github.com/Southampton-RSG/breccia-mapper/issues/35
        ]


class PersonAnswerSetSerializer(base.FlattenedModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = models.PersonAnswerSet
        fields = [
            'id',
            'person',
            'timestamp',
            'replaced_timestamp',
            'nationality',
            'country_of_residence',
            'organisation',
            'organisation_started_date',
            'job_title',
            'disciplines',
            'themes',
            'latitude',
            'longitude',
        ]

    @property
    def column_headers(self) -> typing.List[str]:
        headers = super().column_headers

        # Add questions to columns
        for question in models.PersonQuestion.objects.all():
            headers.append(underscore(question.slug))

        return headers

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        try:
            # Add relationship question answers to data
            for answer in instance.question_answers.all():
                rep[underscore(answer.question.slug)] = underscore(answer.slug)

        except AttributeError:
            pass

        return rep


class RelationshipSerializer(base.FlattenedModelSerializer):
    source = PersonSerializer()
    target = PersonSerializer()

    class Meta:
        model = models.Relationship
        fields = [
            'id',
            'source',
            'target',
        ]


def underscore(slug: str) -> str:
    """Replace hyphens with underscores in text."""
    return slug.replace('-', '_')


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
            headers.append(underscore(question.slug))

        return headers

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        try:
            # Add relationship question answers to data
            for answer in instance.question_answers.all():
                rep[underscore(answer.question.slug)] = underscore(answer.slug)

        except AttributeError:
            pass

        return rep
