"""
Views for displaying or manipulating models in the 'people' app.
"""

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from . import forms, models, permissions


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


class PersonUpdateView(permissions.UserIsLinkedPersonMixin, UpdateView):
    """
    View for updating a :class:`Person` record.
    """
    model = models.Person
    template_name = 'people/person/update.html'
    form_class = forms.PersonForm


class RelationshipDetailView(permissions.UserIsLinkedPersonMixin, DetailView):
    """
    View displaying details of a :class:`Relationship`.
    """
    model = models.Relationship
    template_name = 'people/relationship/detail.html'
    related_person_field = 'source'


class RelationshipCreateView(permissions.UserIsLinkedPersonMixin, CreateView):
    """
    View for creating a :class:`Relationship`.

    Displays / processes a form containing the :class:`RelationshipQuestion`s.
    """
    model = models.Relationship
    template_name = 'people/relationship/create.html'
    fields = [
        'source',
        'target',
    ]

    def get_test_person(self) -> models.Person:
        """
        Get the person instance which should be used for access control checks.
        """
        if self.request.method == 'POST':
            return models.Person.objects.get(pk=self.request.POST.get('source'))

        return models.Person.objects.get(pk=self.kwargs.get('person_pk'))

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

    def get_success_url(self):
        return reverse('people:relationship.update', kwargs={'pk': self.object.pk})


class RelationshipUpdateView(permissions.UserIsLinkedPersonMixin, CreateView):
    """
    View for creating a :class:`Relationship`.

    Displays / processes a form containing the :class:`RelationshipQuestion`s.
    """
    model = models.RelationshipAnswerSet
    template_name = 'people/relationship/update.html'
    form_class = forms.RelationshipAnswerSetForm

    def get_test_person(self) -> models.Person:
        """
        Get the person instance which should be used for access control checks.
        """
        relationship = models.Relationship.objects.get(pk=self.kwargs.get('relationship_pk'))

        return relationship.source

    def get(self, request, *args, **kwargs):
        self.relationship = models.Relationship.objects.get(pk=self.kwargs.get('relationship_pk'))
        self.person = self.relationship.source

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.relationship = models.Relationship.objects.get(pk=self.kwargs.get('relationship_pk'))
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
        Don't rebind self.object to be the result of the form - it is a :class:`RelationshipAnswerSet`.
        """
        form.save()
        
        return HttpResponseRedirect(self.relationship.get_absolute_url())
