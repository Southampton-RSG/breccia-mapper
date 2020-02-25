import typing

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from backports.db.models.enums import TextChoices


class User(AbstractUser):
    """
    Custom user model in case we need to make changes later.
    """


class Organisation(models.Model):
    """
    Organisation to which a :class:`Person` belongs.
    """
    name = models.CharField(max_length=255,
                            blank=False, null=False)
    
    def __str__(self) -> str:
        return self.name
    
    
class Role(models.Model):
    """
    Role which a :class:`Person` holds within the project.
    """
    name = models.CharField(max_length=255,
                            blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Discipline(models.Model):
    """
    Discipline within which a :class:`Person` works.
    """
    name = models.CharField(max_length=255,
                            blank=False, null=False)

    #: Short code using system such as JACS 3
    code = models.CharField(max_length=15,
                            blank=True, null=False)

    def __str__(self) -> str:
        return self.name
    
    
class Theme(models.Model):
    """
    Project theme within which a :class:`Person` works.
    """
    name = models.CharField(max_length=255,
                            blank=False, null=False)

    def __str__(self) -> str:
        return self.name


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
                                blank=True, null=True)

    #: Name of the person
    name = models.CharField(max_length=255,
                            blank=False, null=False)

    #: Is this person a member of the core project team?
    core_member = models.BooleanField(default=False,
                                      blank=False, null=False)

    #: People with whom this person has relationship - via intermediate :class:`Relationship` model
    relationship_targets = models.ManyToManyField('self', related_name='relationship_sources',
                                                  through='Relationship',
                                                  through_fields=('source', 'target'),
                                                  symmetrical=False)

    ###############################################################
    # Data collected for analysis of community makeup and structure

    class GenderChoices(TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
        PREFER_NOT_TO_SAY = 'N', _('Prefer not to say')

    gender = models.CharField(max_length=1,
                              choices=GenderChoices.choices,
                              blank=True, null=False)

    class AgeGroupChoices(TextChoices):
        LTE_25 = '<=25', _('25 or under')
        BETWEEN_26_30 = '26-30', _('26-30')
        BETWEEN_31_35 = '31-35', _('31-35')
        BETWEEN_36_40 = '36-40', _('36-40')
        BETWEEN_41_45 = '41-45', _('41-45')
        BETWEEN_46_50 = '46-50', _('46-50')
        BETWEEN_51_55 = '51-55', _('51-55')
        BETWEEN_56_60 = '56-60', _('56-60')
        GTE_61 = '>=61', _('61 or older')
        PREFER_NOT_TO_SAY = 'N', _('Prefer not to say')

    age_group = models.CharField(max_length=5,
                                 choices=AgeGroupChoices.choices,
                                 blank=True, null=False)
    
    nationality = CountryField(blank=True, null=True)

    country_of_residence = CountryField(blank=True, null=True)

    #: Organisation this person is employed by or affiliated with
    organisation = models.ForeignKey(Organisation,
                                     on_delete=models.PROTECT,
                                     related_name='members',
                                     blank=True, null=True)

    #: Job title this person holds within their organisation
    job_title = models.CharField(max_length=255,
                                 blank=True, null=False)

    #: Discipline within which this person works
    discipline = models.ForeignKey(Discipline,
                                   on_delete=models.PROTECT,
                                   related_name='people',
                                   blank=True, null=True)

    #: Role this person holds within the project
    role = models.ForeignKey(Role,
                             on_delete=models.PROTECT,
                             related_name='holders',
                             blank=True, null=True)

    #: Project themes within this person works
    themes = models.ManyToManyField(Theme,
                                    related_name='people',
                                    blank=True)

    @property
    def relationships(self):
        return self.relationships_as_source.all().union(
            self.relationships_as_target.all()
        )

    def get_absolute_url(self):
        return reverse('people:person.detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.name


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
    text = models.CharField(max_length=1023,
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
    text = models.CharField(max_length=1023,
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

    #: Answers to :class:`RelationshipQuestion`s
    question_answers = models.ManyToManyField(RelationshipQuestionChoice)

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
