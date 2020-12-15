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
    'Organisation',
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


class Organisation(models.Model):
    """
    Organisation to which a :class:`Person` belongs.
    """
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Theme(models.Model):
    """
    Project theme within which a :class:`Person` works.
    """
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class PersonQuestion(Question):
    """Question which may be asked about a person."""


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

    #: Discipline(s) within which this person works
    disciplines = models.CharField(max_length=255, blank=True, null=True)

    #: Project themes within this person works
    themes = models.ManyToManyField(Theme, related_name='people', blank=True)

    #: Latitude for displaying locaiton on a map
    latitude = models.FloatField(blank=True, null=True)

    #: Longitude for displaying locaiton on a map
    longitude = models.FloatField(blank=True, null=True)

    def get_absolute_url(self):
        return self.person.get_absolute_url()
