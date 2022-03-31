"""Base models for configurable questions and response sets."""
import abc
import typing

from django.db import models
from django.utils.text import slugify

__all__ = [
    'Question',
    'QuestionChoice',
]


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

    #: Text of question - 1st person
    text = models.CharField(max_length=255, blank=False, null=False)

    #: Alternative text to be displayed in network filters - 3rd person
    filter_text = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        help_text='Alternative text to be displayed in network filters - 3rd person')

    help_text = models.CharField(
        help_text='Additional hint text to be displayed with the question',
        max_length=255,
        blank=True,
        null=False
    )

    #: Should answers to this question be considered public?
    answer_is_public = models.BooleanField(
        help_text='Should answers to this question be considered public?',
        default=True,
        blank=False,
        null=False)

    #: Should people be able to select multiple responses to this question?
    is_multiple_choice = models.BooleanField(default=False,
                                             blank=False,
                                             null=False)

    @property
    def is_hardcoded(self) -> bool:
        return bool(self.hardcoded_field)

    hardcoded_field = models.CharField(
        help_text='Which hardcoded field does this question represent?',
        max_length=255,
        blank=True,
        null=False
    )

    #: Should people be able to add their own answers?
    allow_free_text = models.BooleanField(default=False,
                                          blank=False,
                                          null=False)

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

    #: Does this answer represent the negative response?
    is_negative_response = models.BooleanField(default=False)

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
        get_latest_by = 'timestamp'

    @classmethod
    @abc.abstractproperty
    def question_model(cls) -> models.Model:
        """Model representing questions to be answered in this AnswerSet."""
        raise NotImplementedError

    #: Entity to which this answer set belongs
    #: This foreign key must be added to each concrete subclass
    # person = models.ForeignKey(Person,
    #                            on_delete=models.CASCADE,
    #                            related_name='answer_sets',
    #                            blank=False,
    #                            null=False)

    @abc.abstractproperty
    def question_answers(self) -> models.QuerySet:
        """Answers to :class:`Question`s.

        This many to many relation must be added to each concrete subclass
        question_answers = models.ManyToManyField(<X>QuestionChoice)
        """
        raise NotImplementedError

    #: When were these answers collected?
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    #: When were these answers replaced? - happens when another set is collected
    replaced_timestamp = models.DateTimeField(blank=True,
                                              null=True,
                                              editable=False)

    @property
    def is_current(self) -> bool:
        return self.replaced_timestamp is None

    def build_question_answers(self,
                               show_all: bool = False,
                               use_slugs: bool = False) -> typing.Dict[str, str]:
        """Collect answers to dynamic questions and join with commas."""
        questions = self.question_model.objects.all()

        if not show_all:
            questions = questions.filter(answer_is_public=True)

        question_answers = {}
        try:
            answerset_answers = list(self.question_answers.order_by().values('text', 'question_id'))

            for question in questions:
                key = question.slug if use_slugs else question.text

                if question.hardcoded_field:
                    answer = getattr(self, question.hardcoded_field)
                    if isinstance(answer, list):
                        answer = ', '.join(map(str, answer))

                else:
                    answer = ', '.join(
                        answer['text'] for answer in answerset_answers
                        if answer['question_id'] == question.id
                    )

                question_answers[key] = answer

        except AttributeError:
            # No AnswerSet yet
            pass

        return question_answers

    def as_dict(self, answers: typing.Optional[typing.Dict[str, typing.Any]] = None):
        """Get the answers from this set as a dictionary for use in Form.initial."""
        if answers is None:
            answers = {}

        for answer in self.question_answers.all():
            question = answer.question
            field_name = f'question_{question.pk}'

            if question.is_multiple_choice:
                if field_name not in answers:
                    answers[field_name] = []

                answers[field_name].append(answer.pk)

            else:
                answers[field_name] = answer.pk

        return answers
