"""Views for displaying or manipulating instances of :class:`Relationship`."""

import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, RedirectView

from people import forms, models, permissions


class RelationshipDetailView(permissions.UserIsLinkedPersonMixin, DetailView):
    """
    View displaying details of a :class:`Relationship`.
    """
    model = models.Relationship
    template_name = 'people/relationship/detail.html'
    related_person_field = 'source'


class RelationshipCreateView(LoginRequiredMixin, RedirectView):
    """View for creating a :class:`Relationship`.

    Redirects to a form containing the :class:`RelationshipQuestion`s.
    """
    def get_redirect_url(self, *args: typing.Any,
                         **kwargs: typing.Any) -> typing.Optional[str]:
        target = models.Person.objects.get(pk=self.kwargs.get('person_pk'))
        relationship, _ = models.Relationship.objects.get_or_create(
            source=self.request.user.person, target=target)

        return reverse('people:relationship.update',
                       kwargs={'relationship_pk': relationship.pk})


class RelationshipUpdateView(permissions.UserIsLinkedPersonMixin, CreateView):
    """
    View for updating the details of a relationship.

    Creates a new :class:`RelationshipAnswerSet` for the :class:`Relationship`.
    Displays / processes a form containing the :class:`RelationshipQuestion`s.
    """
    model = models.RelationshipAnswerSet
    template_name = 'people/relationship/update.html'
    form_class = forms.RelationshipAnswerSetForm

    def get_test_person(self) -> models.Person:
        """
        Get the person instance which should be used for access control checks.
        """
        relationship = models.Relationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))

        return relationship.source

    def get(self, request, *args, **kwargs):
        self.relationship = models.Relationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.relationship = models.Relationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.person
        context['relationship'] = self.relationship

        return context

    def get_initial(self):
        initial = super().get_initial()

        initial['relationship'] = self.relationship

        return initial

    def form_valid(self, form):
        """
        Mark any previous answer sets as replaced.
        """
        response = super().form_valid(form)
        now_date = timezone.now().date()

        # Shouldn't be more than one after initial updates after migration
        for answer_set in self.relationship.answer_sets.exclude(
                pk=self.object.pk):
            answer_set.replaced_timestamp = now_date
            answer_set.save()

        return response


class OrganisationRelationshipDetailView(permissions.UserIsLinkedPersonMixin,
                                         DetailView):
    """View displaying details of an :class:`OrganisationRelationship`."""
    model = models.OrganisationRelationship
    template_name = 'people/organisation-relationship/detail.html'
    related_person_field = 'source'
    context_object_name = 'relationship'


class OrganisationRelationshipCreateView(LoginRequiredMixin, RedirectView):
    """View for creating a :class:`OrganisationRelationship`.

    Redirects to a form containing the :class:`OrganisationRelationshipQuestion`s.
    """
    def get_redirect_url(self, *args: typing.Any,
                         **kwargs: typing.Any) -> typing.Optional[str]:
        target = models.Organisation.objects.get(
            pk=self.kwargs.get('organisation_pk'))
        relationship, _ = models.OrganisationRelationship.objects.get_or_create(
            source=self.request.user.person, target=target)

        return reverse('people:organisation.relationship.update',
                       kwargs={'relationship_pk': relationship.pk})


class OrganisationRelationshipUpdateView(permissions.UserIsLinkedPersonMixin,
                                         CreateView):
    """
    View for updating the details of a Organisationrelationship.

    Creates a new :class:`OrganisationRelationshipAnswerSet` for the :class:`OrganisationRelationship`.
    Displays / processes a form containing the :class:`OrganisationRelationshipQuestion`s.
    """
    model = models.OrganisationRelationshipAnswerSet
    template_name = 'people/relationship/update.html'
    form_class = forms.OrganisationRelationshipAnswerSetForm

    def get_test_person(self) -> models.Person:
        """
        Get the person instance which should be used for access control checks.
        """
        relationship = models.OrganisationRelationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))

        return relationship.source

    def get(self, request, *args, **kwargs):
        self.relationship = models.OrganisationRelationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.relationship = models.OrganisationRelationship.objects.get(
            pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.person
        context['relationship'] = self.relationship

        return context

    def get_initial(self):
        initial = super().get_initial()

        initial['relationship'] = self.relationship

        return initial

    def form_valid(self, form):
        """
        Mark any previous answer sets as replaced.
        """
        response = super().form_valid(form)
        now_date = timezone.now().date()

        # Shouldn't be more than one after initial updates after migration
        for answer_set in self.relationship.answer_sets.exclude(
                pk=self.object.pk):
            answer_set.replaced_timestamp = now_date
            answer_set.save()

        return response
