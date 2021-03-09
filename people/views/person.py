"""
Views for displaying or manipulating instances of :class:`Person`.
"""

import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from people import forms, models, permissions
from .map import get_map_data


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
    """View displaying a list of :class:`Person` objects - searchable."""
    model = models.Person
    template_name = 'people/person/list.html'

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)

        context['existing_relationships'] = set(
            self.request.user.person.relationship_targets.values_list(
                'pk', flat=True))

        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """
    View displaying the profile of a :class:`Person` - who may be a user.
    """
    model = models.Person

    def get_template_names(self) -> typing.List[str]:
        """Return template depending on level of access."""
        if (self.object.user == self.request.user) or self.request.user.is_superuser:
            return ['people/person/detail_full.html']

        return ['people/person/detail_partial.html']

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

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Add current :class:`PersonAnswerSet` to context."""
        context = super().get_context_data(**kwargs)

        context['answer_set'] = self.object.current_answers
        context['map_markers'] = [get_map_data(self.object)]

        return context


class PersonUpdateView(permissions.UserIsLinkedPersonMixin, UpdateView):
    """View for updating a :class:`Person` record."""
    model = models.Person
    context_object_name = 'person'
    template_name = 'people/person/update.html'
    form_class = forms.PersonAnswerSetForm

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)

        context['map_markers'] = [get_map_data(self.object)]

        return context

    def get_initial(self) -> typing.Dict[str, typing.Any]:
        try:
            previous_answers = self.object.current_answers.as_dict()

        except AttributeError:
            previous_answers = {}

        previous_answers.update({
            'person_id': self.object.id,
        })

        return previous_answers

    def get_form_kwargs(self) -> typing.Dict[str, typing.Any]:
        """Remove instance from form kwargs as it's a person, but expects a PersonAnswerSet."""
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')

        return kwargs

    def form_valid(self, form):
        """Mark any previous answer sets as replaced."""
        response = super().form_valid(form)
        now_date = timezone.now().date()

        # Saving the form made self.object a PersonAnswerSet - so go up, then back down
        # Shouldn't be more than one after initial updates after migration
        for answer_set in self.object.person.answer_sets.exclude(
                pk=self.object.pk):
            answer_set.replaced_timestamp = now_date
            answer_set.save()

        return response
