"""
Views for displaying or manipulating models in the 'people' app.
"""

from django.views.generic import DetailView, ListView

from . import models


class PersonListView(ListView):
    """
    View displaying a list of :class:`Person` objects - searchable.
    """
    model = models.Person
    template_name = 'people/person/list.html'


class ProfileView(DetailView):
    """
    View displaying the profile of a :class:`Person` - who may be a user.
    """
    model = models.Person
    template_name = 'people/person/detail.html'


class RelationshipDetailView(DetailView):
    """
    View displaying details of a :class:`Relationship`.
    """
    model = models.Relationship
    template_name = 'people/relationship/detail.html'
