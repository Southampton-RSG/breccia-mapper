"""Base models for configurable questions and response sets."""
import typing

from django.db import models
from django.utils.text import slugify


class Question(models.Model):
    """Questions from which a survey form can be created."""
    class Meta:
        abstract = True
        ordering = [
            'order',
            'text',
        ]

    #: Version number of this question - to allow modification without invalidating existing data
    version = models.PositiveSmallIntegerField(default=1,
                                               blank=False,
                                               null=False)

    #: Text of question
    text = models.CharField(max_length=255, blank=False, null=False)

    #: Position of this question in the list
    order = models.SmallIntegerField(default=0, blank=False, null=False)

    @property
    def choices(self) -> typing.List[typing.List[str]]:
        """Convert the :class:`QuestionChoice`s for this question into Django choices."""
        return [[choice.pk, str(choice)] for choice in self.answers.all()]

    @property
    def slug(self) -> str:
        return slugify(self.text)

    def __str__(self) -> str:
        return self.text


class QuestionChoice(models.Model):
    """Allowed answer to a :class:`Question`."""
    class Meta:
        abstract = True
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
    #: This foreign key must be added to each concrete subclass
    # question = models.ForeignKey(Question,
    #                              related_name='answers',
    #                              on_delete=models.CASCADE,
    #                              blank=False,
    #                              null=False)

    #: Text of answer
    text = models.CharField(max_length=255, blank=False, null=False)

    #: Position of this answer in the list
    order = models.SmallIntegerField(default=0, blank=False, null=False)

    @property
    def slug(self) -> str:
        return slugify(self.text)

    def __str__(self) -> str:
        return self.text


class AnswerSet(models.Model):
    """The answers to a set of questions at a particular point in time."""
    class Meta:
        abstract = True
        ordering = [
            'timestamp',
        ]

    #: Entity to which this answer set belongs
    #: This foreign key must be added to each concrete subclass
    # person = models.ForeignKey(Person,
    #                            on_delete=models.CASCADE,
    #                            related_name='answer_sets',
    #                            blank=False,
    #                            null=False)

    #: Answers to :class:`Question`s
    #: This many to many relation must be added to each concrete subclass
    # question_answers = models.ManyToManyField(QuestionChoice)

    #: When were these answers collected?
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    #: When were these answers replaced? - happens when another set is collected
    replaced_timestamp = models.DateTimeField(blank=True,
                                              null=True,
                                              editable=False)
