import typing

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """
    Custom user model in case we need to make changes later.
    """


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
