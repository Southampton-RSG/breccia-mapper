"""
Views for displaying networks of :class:`People` and :class:`Relationship`s.
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import ValidationError
from django.utils import timezone
from django.views.generic import FormView

from people import forms, models, serializers

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


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
        form: forms.NetworkFilterForm = context['form']
        if not form.is_valid():
            return context

        at_date = form.cleaned_data['date']
        if not at_date:
            at_date = timezone.now().date()

        # Filter on timestamp__date doesn't seem to work on MySQL
        # To compare datetimes we need at_date to be midnight at
        # the *end* of the day in question - so add one day here
        at_date += timezone.timedelta(days=1)

        relationship_answerset_set = models.RelationshipAnswerSet.objects.filter(
            Q(replaced_timestamp__gte=at_date)
            | Q(replaced_timestamp__isnull=True),
            timestamp__lte=at_date)

        logger.info('Found %d relationship answer sets for %s',
                    relationship_answerset_set.count(), at_date)

        # Filter answers to relationship questions
        for field, values in form.cleaned_data.items():
            if field.startswith('question_') and values:
                relationship_answerset_set = relationship_answerset_set.filter(
                    question_answers__in=values)

        logger.info('Found %d relationship answer sets matching filters',
                    relationship_answerset_set.count())

        context['person_set'] = serializers.PersonSerializer(
            models.Person.objects.all(), many=True).data

        context['organisation_set'] = serializers.OrganisationSerializer(
            models.Organisation.objects.all(), many=True).data

        context['relationship_set'] = serializers.RelationshipSerializer(
            models.Relationship.objects.filter(
                pk__in=relationship_answerset_set.values_list('relationship',
                                                              flat=True)),
            many=True).data

        logger.info('Found %d distinct relationships matching filters',
                    len(context['relationship_set']))

        return context

    def form_valid(self, form):
        try:
            return self.render_to_response(self.get_context_data())

        except ValidationError:
            return self.form_invalid(form)
