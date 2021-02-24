import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from django_settings_export import settings_export
from post_office import mail

from .question import AnswerSet, Question, QuestionChoice

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

__all__ = [
    'User',
    'OrganisationQuestion',
    'OrganisationQuestionChoice',
    'Organisation',
    'OrganisationAnswerSet',
    'Theme',
    'PersonQuestion',
    'PersonQuestionChoice',
    'Person',
    'PersonAnswerSet',
]


class User(AbstractUser):
    """
    Custom user model in case we need to make changes later.
    """
    email = models.EmailField(_('email address'), blank=False, null=False)

    #: Have they given consent to collect and store their data?
    consent_given = models.BooleanField(default=False)

    def has_person(self) -> bool:
        """
        Does this user have a linked :class:`Person` record?
        """
        return hasattr(self, 'person')

    def send_welcome_email(self) -> None:
        """Send a welcome email to a new user."""
        # Get exported data from settings.py first
        context = settings_export(None)
        context.update({
            'user': self,
        })

        logger.info('Sending welcome mail to user \'%s\'', self.username)

        try:
            mail.send(
                [self.email],
                sender=settings.DEFAULT_FROM_EMAIL,
                template=settings.TEMPLATE_WELCOME_EMAIL_NAME,
                context=context,
                priority='now'  # Send immediately - don't add to queue
            )

        except ValidationError:
            logger.error(
                'Sending welcome mail failed, invalid email for user \'%s\'',
                self.username)


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

    #: Latitude for displaying location on a map
    latitude = models.FloatField(blank=True, null=True)

    #: Longitude for displaying location on a map
    longitude = models.FloatField(blank=True, null=True)

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

    #: Answers to :class:`OrganisationQuestion`s
    question_answers = models.ManyToManyField(OrganisationQuestionChoice)

    def public_answers(self) -> models.QuerySet:
        """Get answers to questions which are public."""
        return self.question_answers.filter(question__answer_is_public=True)

    def as_dict(self):
        """Get the answers from this set as a dictionary for use in Form.initial."""
        exclude_fields = {
            'id',
            'timestemp',
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


class Theme(models.Model):
    """
    Project theme within which a :class:`Person` works.
    """
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class PersonQuestion(Question):
    """Question which may be asked about a person."""
    #: Should answers to this question be displayed on public profiles?
    answer_is_public = models.BooleanField(
        help_text='Should answers to this question be displayed on profiles?',
        default=True,
        blank=False,
        null=False)


class PersonQuestionChoice(QuestionChoice):
    """Allowed answer to a :class:`PersonQuestion`."""
    #: Question to which this answer belongs
    question = models.ForeignKey(PersonQuestion,
                                 related_name='answers',
                                 on_delete=models.CASCADE,
                                 blank=False,
                                 null=False)


class Person(models.Model):
    """
    A person may be a member of the BRECcIA core team or an external stakeholder.
    """
    class Meta:
        verbose_name_plural = 'people'
        ordering = [
            'name',
        ]

    #: User account belonging to this person
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='person',
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)

    #: Name of the person
    name = models.CharField(max_length=255, blank=False, null=False)

    #: People with whom this person has relationship - via intermediate :class:`Relationship` model
    relationship_targets = models.ManyToManyField(
        'self',
        related_name='relationship_sources',
        through='Relationship',
        through_fields=('source', 'target'),
        symmetrical=False)

    @property
    def relationships(self):
        return self.relationships_as_source.all().union(
            self.relationships_as_target.all())

    @property
    def current_answers(self) -> 'PersonAnswerSet':
        return self.answer_sets.last()

    def get_absolute_url(self):
        return reverse('people:person.detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.name


class PersonAnswerSet(AnswerSet):
    """The answers to the person questions at a particular point in time."""
    #: Person to which this answer set belongs
    person = models.ForeignKey(Person,
                               on_delete=models.CASCADE,
                               related_name='answer_sets',
                               blank=False,
                               null=False)

    #: Answers to :class:`PersonQuestion`s
    question_answers = models.ManyToManyField(PersonQuestionChoice)

    ##################
    # Static questions

    nationality = CountryField(blank=True, null=True)

    country_of_residence = CountryField(blank=True, null=True)

    #: Organisation this person is employed by or affiliated with
    organisation = models.ForeignKey(Organisation,
                                     on_delete=models.PROTECT,
                                     related_name='members',
                                     blank=True,
                                     null=True)

    #: When did this person start at their current organisation?
    organisation_started_date = models.DateField(
        'Date started at this organisation', blank=False, null=True)

    #: Job title this person holds within their organisation
    job_title = models.CharField(max_length=255, blank=True, null=False)

    #: Project themes within this person works
    themes = models.ManyToManyField(Theme, related_name='people', blank=True)

    #: Latitude for displaying location on a map
    latitude = models.FloatField(blank=True, null=True)

    #: Longitude for displaying location on a map
    longitude = models.FloatField(blank=True, null=True)

    def public_answers(self) -> models.QuerySet:
        """Get answers to questions which are public."""
        return self.question_answers.filter(question__answer_is_public=True)

    def as_dict(self):
        """Get the answers from this set as a dictionary for use in Form.initial."""
        exclude_fields = {
            'id',
            'timestemp',
            'replaced_timestamp',
            'person_id',
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
        return self.person.get_absolute_url()
