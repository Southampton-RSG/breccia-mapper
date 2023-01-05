"""Models describing relationships between people."""

import typing

from django.db import models
from django.urls import reverse

from .person import Organisation, Person
from .question import AnswerSet, Question, QuestionChoice

__all__ = [
    'RelationshipQuestion',
    'RelationshipQuestionChoice',
    'RelationshipAnswerSet',
    'Relationship',
    'OrganisationRelationshipQuestion',
    'OrganisationRelationshipQuestionChoice',
    'OrganisationRelationshipAnswerSet',
    'OrganisationRelationship',
]


class RelationshipQuestion(Question):
    """Question which may be asked about a relationship."""


class RelationshipQuestionChoice(QuestionChoice):
    """Allowed answer to a :class:`RelationshipQuestion`."""

    #: Question to which this answer belongs
    question = models.ForeignKey(RelationshipQuestion,
                                 related_name='answers',
                                 on_delete=models.CASCADE,
                                 blank=False,
                                 null=False)
    class Meta(QuestionChoice.Meta):
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'],
                                    name='unique_question_answer_relationshipquestionchoice')
        ]


class Relationship(models.Model):
    """A directional relationship between two people allowing linked questions."""
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'target'],
                                    name='unique_relationship_modelrelationship'),
        ]

    #: Person reporting the relationship
    source = models.ForeignKey(Person,
                               related_name='relationships_as_source',
                               on_delete=models.CASCADE,
                               blank=False,
                               null=False)

    #: Person with whom the relationship is reported
    target = models.ForeignKey(Person,
                               related_name='relationships_as_target',
                               on_delete=models.CASCADE,
                               blank=False,
                               null=False)

    @property
    def current_answers(self) -> typing.Optional['RelationshipAnswerSet']:
        try:
            answer_set = self.answer_sets.latest()
            if answer_set.is_current:
                return answer_set

        except RelationshipAnswerSet.DoesNotExist:
            # No AnswerSet created yet
            pass

        return None

    @property
    def is_current(self) -> bool:
        return self.current_answers is not None

    def get_absolute_url(self):
        return reverse('people:relationship.detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return f'{self.source} -> {self.target}'

    @property
    def reverse(self):
        """
        Get the reverse of this relationship.

        @raise Relationship.DoesNotExist: When the reverse relationship is not known
        """
        return type(self).objects.get(source=self.target, target=self.source)


class RelationshipAnswerSet(AnswerSet):
    """The answers to the relationship questions at a particular point in time."""

    question_model = RelationshipQuestion

    #: Relationship to which this answer set belongs
    relationship = models.ForeignKey(Relationship,
                                     on_delete=models.CASCADE,
                                     related_name='answer_sets',
                                     blank=False,
                                     null=False)

    #: Answers to :class:`RelationshipQuestion`s
    question_answers = models.ManyToManyField(RelationshipQuestionChoice)

    def get_absolute_url(self):
        return self.relationship.get_absolute_url()


class OrganisationRelationshipQuestion(Question):
    """Question which may be asked about an :class:`OrganisationRelationship`."""


class OrganisationRelationshipQuestionChoice(QuestionChoice):
    """Allowed answer to a :class:`OrganisationRelationshipQuestion`."""

    #: Question to which this answer belongs
    question = models.ForeignKey(OrganisationRelationshipQuestion,
                                 related_name='answers',
                                 on_delete=models.CASCADE,
                                 blank=False,
                                 null=False)
    class Meta(QuestionChoice.Meta):
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'],
                                    name='unique_question_answer_organisationrelationshipquestionchoice')
        ]


class OrganisationRelationship(models.Model):
    """A directional relationship between a person and an organisation with linked questions."""
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'target'],
                                    name='unique_relationship_modelorganisationrelationship'),
        ]

    #: Person reporting the relationship
    source = models.ForeignKey(
        Person,
        related_name='organisation_relationships_as_source',
        on_delete=models.CASCADE,
        blank=False,
        null=False)

    #: Organisation with which the relationship is reported
    target = models.ForeignKey(
        Organisation,
        related_name='organisation_relationships_as_target',
        on_delete=models.CASCADE,
        blank=False,
        null=False)

    @property
    def current_answers(self) -> typing.Optional['OrganisationRelationshipAnswerSet']:
        try:
            answer_set = self.answer_sets.latest()
            if answer_set.is_current:
                return answer_set

        except OrganisationRelationshipAnswerSet.DoesNotExist:
            # No AnswerSet created yet
            pass

        return None

    @property
    def is_current(self) -> bool:
        return self.current_answers is not None

    def get_absolute_url(self):
        return reverse('people:organisation.relationship.detail',
                       kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return f'{self.source} -> {self.target}'


class OrganisationRelationshipAnswerSet(AnswerSet):
    """The answers to the organisation relationship questions at a particular point in time."""

    question_model = OrganisationRelationshipQuestion

    #: OrganisationRelationship to which this answer set belongs
    relationship = models.ForeignKey(OrganisationRelationship,
                                     on_delete=models.CASCADE,
                                     related_name='answer_sets',
                                     blank=False,
                                     null=False)

    #: Answers to :class:`OrganisationRelationshipQuestion`s
    question_answers = models.ManyToManyField(
        OrganisationRelationshipQuestionChoice)

    def get_absolute_url(self):
        return self.relationship.get_absolute_url()
