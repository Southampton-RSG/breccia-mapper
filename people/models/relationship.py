"""
Models describing relationships between people.
"""

import typing

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .person import Person

__all__ = [
    'RelationshipQuestion',
    'RelationshipQuestionChoice',
    'RelationshipAnswerSet',
    'Relationship',
]


class RelationshipQuestion(models.Model):
    """
    Question which may be asked about a relationship.
    """
    class Meta:
        ordering = [
            'order',
            'text',
        ]

    #: Version number of this question - to allow modification without invalidating existing data
    version = models.PositiveSmallIntegerField(default=1,
                                               blank=False, null=False)

    #: Text of question
    text = models.CharField(max_length=255,
                            blank=False, null=False)

    #: Position of this question in the list
    order = models.SmallIntegerField(default=0,
                                     blank=False, null=False)

    @property
    def choices(self) -> typing.List[typing.List[str]]:
        """
        Convert the :class:`RelationshipQuestionChoice`s for this question into Django choices.
        """
        return [
            [choice.pk, str(choice)] for choice in self.answers.all()
        ]

    @property
    def slug(self) -> str:
        return slugify(self.text)

    def __str__(self) -> str:
        return self.text


class RelationshipQuestionChoice(models.Model):
    """
    Allowed answer to a :class:`RelationshipQuestion`.
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'],
                                    name='unique_question_answer')
        ]
        ordering = [
            'question__order',
            'order',
            'text',
        ]

    #: Question to which this answer belongs
    question = models.ForeignKey(RelationshipQuestion, related_name='answers',
                                 on_delete=models.CASCADE,
                                 blank=False, null=False)

    #: Text of answer
    text = models.CharField(max_length=255,
                            blank=False, null=False)

    #: Position of this answer in the list
    order = models.SmallIntegerField(default=0,
                                     blank=False, null=False)

    @property
    def slug(self) -> str:
        return slugify(self.text)

    def __str__(self) -> str:
        return self.text


# class ExternalPerson(models.Model):
#     """Model representing a person external to the project.

#     These will never need to be linked to a :class:`User` as they
#     will never log in to the system.
#     """
#     name = models.CharField(max_length=255,
#                             blank=False, null=False)

#     def __str__(self) -> str:
#         return self.name


class Relationship(models.Model):
    """
    A directional relationship between two people allowing linked questions.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'target_person'],
                                    name='unique_relationship'),
        ]

    #: Person reporting the relationship
    source = models.ForeignKey(Person, related_name='relationships_as_source',
                               on_delete=models.CASCADE,
                               blank=False, null=False)

    #: Person with whom the relationship is reported
    target_person = models.ForeignKey(Person,
                                      related_name='relationships_as_target',
                                      on_delete=models.CASCADE,
                                      blank=False,
                                      null=False)
                                    #   blank=True,
                                    #   null=True)

    # target_external_person = models.ForeignKey(
    #     ExternalPerson,
    #     related_name='relationships_as_target',
    #     on_delete=models.CASCADE,
    #     blank=True,
    #     null=True)

    #: When was this relationship defined?
    created = models.DateTimeField(auto_now_add=True)

    #: When was this marked as expired?  Default None means it has not expired
    expired = models.DateTimeField(blank=True, null=True)

    @property
    def target(self) -> Person:
        if self.target_person:
            return self.target_person

        raise ObjectDoesNotExist('Relationship has no target linked')

    @property
    def current_answers(self) -> 'RelationshipAnswerSet':
        return self.answer_sets.last()

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
        return type(self).objects.get(source=self.target_person,
                                      target_person=self.source)


class RelationshipAnswerSet(models.Model):
    """
    The answers to the relationship questions at a particular point in time.
    """

    class Meta:
        ordering = [
            'timestamp',
        ]

    #: Relationship to which this answer set belongs
    relationship = models.ForeignKey(Relationship,
                                     on_delete=models.CASCADE,
                                     related_name='answer_sets',
                                     blank=False, null=False)

    #: Answers to :class:`RelationshipQuestion`s
    question_answers = models.ManyToManyField(RelationshipQuestionChoice)

    #: When were these answers collected?
    timestamp = models.DateTimeField(auto_now_add=True,
                                     editable=False)

    replaced_timestamp = models.DateTimeField(blank=True, null=True,
                                              editable=False)

    def get_absolute_url(self):
        return self.relationship.get_absolute_url()
