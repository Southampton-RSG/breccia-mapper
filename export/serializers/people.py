import typing

from people import models

from . import base


def underscore(slug: str) -> str:
    """Replace hyphens with underscores in text."""
    return slug.replace('-', '_')


def underscore_dict_keys(dict_: typing.Mapping[str, typing.Any]):
    return {underscore(key): value for key, value in dict_.items()}


class AnswerSetSerializer(base.FlattenedModelSerializer):
    question_model = None

    @property
    def column_headers(self) -> typing.List[str]:
        headers = super().column_headers

        # Add relationship questions to columns
        for question in self.question_model.objects.all():
            headers.append(underscore(question.slug))

        return headers

    def to_representation(self, instance: models.question.AnswerSet):
        rep = super().to_representation(instance)

        rep.update(
            underscore_dict_keys(instance.build_question_answers(use_slugs=True, show_all=True))
        )

        return rep


class PersonSerializer(base.FlattenedModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'id',
            'name',
        ]


class PersonAnswerSetSerializer(AnswerSetSerializer):
    question_model = models.PersonQuestion
    person = PersonSerializer()

    class Meta:
        model = models.PersonAnswerSet
        fields = [
            'id',
            'person',
            'timestamp',
            'replaced_timestamp',
            'latitude',
            'longitude',
        ]


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


class RelationshipAnswerSetSerializer(AnswerSetSerializer):
    question_model = models.RelationshipQuestion
    relationship = RelationshipSerializer()

    class Meta:
        model = models.RelationshipAnswerSet
        fields = [
            'id',
            'relationship',
            'timestamp',
            'replaced_timestamp',
        ]


class OrganisationSerializer(base.FlattenedModelSerializer):
    class Meta:
        model = models.Organisation
        fields = [
            'id',
            'name',
        ]


class OrganisationAnswerSetSerializer(AnswerSetSerializer):
    question_model = models.OrganisationQuestion
    organisation = OrganisationSerializer()

    class Meta:
        model = models.OrganisationAnswerSet
        fields = [
            'id',
            'organisation',
            'timestamp',
            'replaced_timestamp',
            'latitude',
            'longitude',
        ]


class OrganisationRelationshipSerializer(base.FlattenedModelSerializer):
    source = OrganisationSerializer()
    target = OrganisationSerializer()

    class Meta:
        model = models.OrganisationRelationship
        fields = [
            'id',
            'source',
            'target',
        ]


class OrganisationRelationshipAnswerSetSerializer(AnswerSetSerializer):
    question_model = models.OrganisationRelationshipQuestion
    relationship = OrganisationRelationshipSerializer()

    class Meta:
        model = models.OrganisationRelationshipAnswerSet
        fields = [
            'id',
            'relationship',
            'timestamp',
            'replaced_timestamp',
        ]
