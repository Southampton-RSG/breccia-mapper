"""
Models describing relationships between people.
"""

import typing

from django.db import models
from django.urls import reverse

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
        Convert the :class:`RelationshipQuestionChoices` for this question into Django choices.
        """
        return [
            [choice.pk, str(choice)] for choice in self.answers.all()
        ]

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

    def __str__(self) -> str:
        return self.text


class Relationship(models.Model):
    """
    A directional relationship between two people allowing linked questions.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'target'],
                                    name='unique_relationship'),
        ]

    #: Person reporting the relationship
    source = models.ForeignKey(Person, related_name='relationships_as_source',
                               on_delete=models.CASCADE,
                               blank=False, null=False)

    #: Person with whom the relationship is reported
    target = models.ForeignKey(Person, related_name='relationships_as_target',
                               on_delete=models.CASCADE,
                               blank=False, null=False)
    
    #: When was this relationship defined?
    created = models.DateTimeField(auto_now_add=True)
    
    #: When was this marked as expired?  Default None means it has not expired
    expired = models.DateTimeField(blank=True, null=True)

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
        return type(self).objects.get(source=self.target,
                                      target=self.source)


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