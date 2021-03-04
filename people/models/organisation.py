import logging

from django.db import models
from django.urls import reverse


from .question import AnswerSet, Question, QuestionChoice

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

__all__ = [
    'OrganisationQuestion',
    'OrganisationQuestionChoice',
    'Organisation',
    'OrganisationAnswerSet',
]


class OrganisationQuestion(Question):
    """Question which may be asked about a Organisation."""
    #: Should answers to this question be displayed on public profiles?
    answer_is_public = models.BooleanField(
        help_text='Should answers to this question be displayed on profiles?',
        default=True,
        blank=False,
        null=False)


class OrganisationQuestionChoice(QuestionChoice):
    """Allowed answer to a :class:`OrganisationQuestion`."""
    #: Question to which this answer belongs
    question = models.ForeignKey(OrganisationQuestion,
                                 related_name='answers',
                                 on_delete=models.CASCADE,
                                 blank=False,
                                 null=False)


class Organisation(models.Model):
    """Organisation to which a :class:`Person` belongs."""
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        return self.name

    @property
    def current_answers(self) -> 'OrganisationAnswerSet':
        return self.answer_sets.last()

    def get_absolute_url(self):
        return reverse('people:organisation.detail', kwargs={'pk': self.pk})


class OrganisationAnswerSet(AnswerSet):
    """The answers to the organisation questions at a particular point in time."""
    #: Organisation to which this answer set belongs
    organisation = models.ForeignKey(Organisation,
                                     on_delete=models.CASCADE,
                                     related_name='answer_sets',
                                     blank=False,
                                     null=False)

    #: Latitude for displaying location on a map
    latitude = models.FloatField(blank=True, null=True)

    #: Longitude for displaying location on a map
    longitude = models.FloatField(blank=True, null=True)

    #: Answers to :class:`OrganisationQuestion`s
    question_answers = models.ManyToManyField(OrganisationQuestionChoice)

    def public_answers(self) -> models.QuerySet:
        """Get answers to questions which are public."""
        return self.question_answers.filter(question__answer_is_public=True)

    def as_dict(self):
        """Get the answers from this set as a dictionary for use in Form.initial."""
        exclude_fields = {
            'id',
            'timestamp',
            'replaced_timestamp',
            'organisation_id',
            'question_answers',
        }

        def field_value_repr(field):
            """Get the representation of a field's value as required by Form.initial."""
            attr_val = getattr(self, field.attname)

            # Relation fields need to return PKs
            if isinstance(field, models.ManyToManyField):
                return [obj.pk for obj in attr_val.all()]

            # But foreign key fields are a PK already so no extra work

            return attr_val

        answers = {
            # Foreign key fields have _id at end in model _meta but don't in forms
            field.attname.rstrip('_id'): field_value_repr(field)
            for field in self._meta.get_fields()
            if field.attname not in exclude_fields
        }

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

    def get_absolute_url(self):
        return self.organisation.get_absolute_url()
