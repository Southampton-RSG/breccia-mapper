import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from people import forms, models


class OrganisationCreateView(LoginRequiredMixin, CreateView):
    """View to create a new instance of :class:`Organisation`."""
    model = models.Organisation
    template_name = 'people/organisation/create.html'
    form_class = forms.OrganisationForm


class OrganisationListView(LoginRequiredMixin, ListView):
    """View displaying a list of :class:`organisation` objects."""
    model = models.Organisation
    template_name = 'people/organisation/list.html'


class OrganisationDetailView(LoginRequiredMixin, DetailView):
    """View displaying details of a :class:`Organisation`."""
    model = models.Organisation
    context_object_name = 'organisation'
    template_name = 'people/organisation/detail.html'

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Add map marker to context."""
        context = super().get_context_data(**kwargs)

        context['map_markers'] = [{
            'name': self.object.name,
            'lat': self.object.latitude,
            'lng': self.object.longitude,
        }]

        return context


class OrganisationUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a :class:`Organisation` record."""
    model = models.Organisation
    context_object_name = 'organisation'
    template_name = 'people/organisation/update.html'
    form_class = forms.OrganisationForm

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Add map marker to context."""
        context = super().get_context_data(**kwargs)

        context['map_markers'] = [{
            'name': self.object.name,
            'lat': self.object.latitude,
            'lng': self.object.longitude,
        }]

        return context
