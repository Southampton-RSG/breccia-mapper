"""
Views for displaying or manipulating models in the 'people' app.
"""

from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, ListView

from . import forms, models


class PersonCreateView(CreateView):
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

    def get_object(self, queryset=None) -> models.Person:
        """
        Get the :class:`Person` object to be represented by this page.

        If not determined from url get current user.
        """
        try:
            return super().get_object(queryset)

        except AttributeError:
            return self.request.user.person


class RelationshipDetailView(DetailView):
    """
    View displaying details of a :class:`Relationship`.
    """
    model = models.Relationship
    template_name = 'people/relationship/detail.html'
    

class RelationshipCreateView(CreateView):
    """
    View for creating a :class:`Relationship`.

    Displays / processes a form containing the :class:`RelationshipQuestion`s.
    """
    model = models.Relationship
    template_name = 'people/relationship/create.html'
    form_class = forms.RelationshipForm
    
    def get(self, request, *args, **kwargs):
        self.person = models.Person.objects.get(pk=self.kwargs.get('person_pk'))

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.person = models.Person.objects.get(pk=self.kwargs.get('person_pk'))

        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        initial['source'] = self.request.user.person
        initial['target'] = self.person

        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.person

        return context
    
    def form_valid(self, form):
        """
        Form is valid - create :class:`Relationship` and save answers to questions.
        """
        self.object = form.save()
        
        return HttpResponseRedirect(self.object.get_absolute_url())

