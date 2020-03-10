"""
Views for displaying or manipulating models in the 'people' app.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from rest_framework.views import APIView, Response

from . import forms, models, permissions, serializers


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
        Mark any previous answer sets as replaced.
        """
        previous_valid_answer_sets = self.relationship.answer_sets.filter(replaced_timestamp__isnull=True)

        response = super().form_valid(form)

        # Shouldn't be more than one after initial updates after migration
        for answer_set in previous_valid_answer_sets:
            answer_set.replaced_timestamp = timezone.now()
            answer_set.save()

        return response
    

class PersonApiView(APIView):
    """
    List all :class:`Person` instances.
    """
    def get(self, request, format=None):
        """
        List all :class:`Person` instances.
        """
        serializer = serializers.PersonSerializer(models.Person.objects.all(),
                                                  many=True)
        return Response(serializer.data)
    
    
class RelationshipApiView(APIView):
    """
    List all :class:`Relationship` instances.
    """
    def get(self, request, format=None):
        """
        List all :class:`Relationship` instances.
        """
        serializer = serializers.RelationshipSerializer(models.Relationship.objects.all(),
                                                        many=True)
        return Response(serializer.data)
    
    
class NetworkView(LoginRequiredMixin, FormView):
    """
    View to display relationship network.
    """
    template_name = 'people/network.html'
    form_class = forms.NetworkFilterForm
    
    def get_form_kwargs(self):
        """
        Add GET params to form data.
        """
        kwargs = super().get_form_kwargs()
        
        if self.request.method == 'GET':
            if 'data' in kwargs:
                kwargs['data'].update(self.request.GET)
            
            else:
                kwargs['data'] = self.request.GET

        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Add filtered QuerySets of :class:`Person` and :class:`Relationship` to the context.
        """
        context = super().get_context_data(**kwargs)
        form = context['form']
        
        at_time = timezone.now()
        
        relationship_set = models.Relationship.objects.all()
        
        # Filter answers to relationship questions
        for key, value in form.data.items():
            if key.startswith('question_') and value:
                question_id = key.replace('question_', '', 1)
                answer = models.RelationshipQuestionChoice.objects.get(pk=value,
                                                                       question__pk=question_id)
                relationship_set = relationship_set.filter(
                    Q(answer_sets__replaced_timestamp__gt=at_time) | Q(answer_sets__replaced_timestamp__isnull=True),
                    answer_sets__timestamp__lte=at_time,
                    answer_sets__question_answers=answer
                )

        context['person_set'] = serializers.PersonSerializer(
            models.Person.objects.all(),
            many=True
        ).data

        context['relationship_set'] = serializers.RelationshipSerializer(
            relationship_set,
            many=True
        ).data
        
        return context
    
    def form_valid(self, form):
        return self.render_to_response(self.get_context_data())
