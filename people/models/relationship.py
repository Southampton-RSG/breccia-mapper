"""
Models describing relationships between people.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse

from .person import Person
from .question import AnswerSet, Question, QuestionChoice

__all__ = [
    'RelationshipQuestion',
    'RelationshipQuestionChoice',
    'RelationshipAnswerSet',
    'Relationship',
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
            models.UniqueConstraint(fields=['source', 'person'],
                                    name='unique_relationship'),
        ]

    #: Person reporting the relationship
    source = models.ForeignKey(Person, related_name='relationships_as_source',
                               on_delete=models.CASCADE,
                               blank=False, null=False)

    #: Person with whom the relationship is reported
    target = models.ForeignKey(Person,
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


class RelationshipAnswerSet(AnswerSet):
    """The answers to the relationship questions at a particular point in time."""

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
