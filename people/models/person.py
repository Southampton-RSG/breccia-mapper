import typing

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from backports.db.models.enums import TextChoices

__all__ = [
    'User',
    'Organisation',
    'Role',
    'Discipline',
    'Theme',
    'Person',
]


class User(AbstractUser):
    """
    Custom user model in case we need to make changes later.
    """
    def has_person(self) -> bool:
        """
        Does this user have a linked :class:`Person` record?
        """
        try:
            person = self.person
            return True

        except AttributeError:
            return False


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

