import typing

from rest_framework import serializers

from people import models

from . import base


class SimplePersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'pk',
            'name',
        ]


class PersonSerializer(base.FlattenedModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'pk',
            'name',
            'core_member',
            'gender',
            'age_group',
            'nationality',
            'country_of_residence',
        ]


class RelationshipSerializer(base.FlattenedModelSerializer):
    source = SimplePersonSerializer()
    target = SimplePersonSerializer()

    class Meta:
        model = models.Relationship
        fields = [
            'pk',
            'source',
            'target',
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
            for answer in instance.current_answers.question_answers.all():
                rep[answer.question.slug.replace('-', '_')] = answer.slug.replace('-', '_')

        except AttributeError:
            pass

        return rep