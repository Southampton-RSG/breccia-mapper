"""
Views for displaying or manipulating instances of :class:`Relationship`.
"""

from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView

from rest_framework.views import APIView, Response

from people import forms, models, permissions, serializers


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
        return reverse('people:relationship.update', kwargs={'relationship_pk': self.object.pk})


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
