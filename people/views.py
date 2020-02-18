"""
Views for displaying or manipulating models in the 'people' app.
"""

from django.views.generic import DetailView

from . import models


class ProfileView(DetailView):
    """
    View displaying the profile of a :class:`Person` - who may be a user.
    """
    model = models.Person
    template_name = 'people/person/detail.html'
    context_object_name = 'person'


class RelationshipDetailView(DetailView):
    """
    View displaying details of a :class:`Relationship`.
    """
    model = models.Relationship
    template_name = 'people/relationship/detail.html'
    context_object_name = 'relationship'
