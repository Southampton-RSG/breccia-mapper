"""
Views for displaying or manipulating instances of :class:`Person`.
"""

import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from people import forms, models, permissions


class PersonCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new instance of :class:`Person`.

    If 'user' is passed as a URL parameter - link the new person to the current user.
    """
    model = models.Person
    template_name = 'people/person/create.html'
    form_class = forms.PersonForm

    def form_valid(self, form):
        if 'user' in self.request.GET:
            form.instance.user = self.request.user

        return super().form_valid(form)


class PersonListView(LoginRequiredMixin, ListView):
    """
    View displaying a list of :class:`Person` objects - searchable.
    """
    model = models.Person
    template_name = 'people/person/list.html'


class ProfileView(permissions.UserIsLinkedPersonMixin, DetailView):
    """
    View displaying the profile of a :class:`Person` - who may be a user.
    """
    model = models.Person
    template_name = 'people/person/detail.html'

    def get_object(self, queryset=None) -> models.Person:
        """
        Get the :class:`Person` object to be represented by this page.

        If not determined from url get current user.
        """
        try:
            return super().get_object(queryset)

        except AttributeError:
            # pk was not provided in URL
            return self.request.user.person

    def get_context_data(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Add current :class:`PersonAnswerSet` to context."""
        context = super().get_context_data(**kwargs)

        context['answer_set'] = self.object.current_answers
        context['map_markers'] = [get_map_data(self.object)]

        return context


class PersonUpdateView(permissions.UserIsLinkedPersonMixin, UpdateView):
    """View for updating a :class:`Person` record."""
    model = models.PersonAnswerSet
    template_name = 'people/person/update.html'
    form_class = forms.PersonAnswerSetForm

    def get_test_person(self) -> models.Person:
        """Get the person instance which should be used for access control checks."""
        return models.Person.objects.get(pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        self.person = models.Person.objects.get(pk=self.kwargs.get('pk'))

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.person = models.Person.objects.get(pk=self.kwargs.get('pk'))

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.person

        return context

    def form_valid(self, form):
        """Mark any previous answer sets as replaced."""
        response = super().form_valid(form)
        now_date = timezone.now().date()

        # Shouldn't be more than one after initial updates after migration
        for answer_set in self.person.answer_sets.exclude(pk=self.object.pk):
            answer_set.replaced_timestamp = now_date
            answer_set.save()

        return response


def get_map_data(person: models.Person) -> typing.Dict[str, typing.Any]:
    answer_set = person.current_answers
    try:
        latitude = answer_set.latitude or None
        longitude = answer_set.longitude or None

    except AttributeError:
        latitude = None
        longitude = None

    return {
        'name': person.name,
        'lat': latitude,
        'lng': longitude,
        'url': reverse('people:person.detail', kwargs={'pk': person.pk})
    }


class PersonMapView(LoginRequiredMixin, ListView):
    """
    View displaying a map of :class:`Person` locations.
    """
    model = models.Person
    template_name = 'people/person/map.html'

    def get_context_data(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)

        context['map_markers'] = [
            get_map_data(person) for person in self.object_list
        ]

        return context
