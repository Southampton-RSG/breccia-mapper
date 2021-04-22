"""
Views for displaying networks of :class:`People` and :class:`Relationship`s.
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import ValidationError
from django.utils import timezone
from django.views.generic import TemplateView

from people import forms, models, serializers

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def filter_relationships(form, at_date):
    relationship_answerset_set = models.RelationshipAnswerSet.objects.filter(
        Q(replaced_timestamp__gte=at_date)
        | Q(replaced_timestamp__isnull=True),
        timestamp__lte=at_date)

    # Filter answers to relationship questions
    for field, values in form.cleaned_data.items():
        if field.startswith(f'{form.question_prefix}question_') and values:
            relationship_answerset_set = relationship_answerset_set.filter(
                question_answers__in=values)

    return models.Relationship.objects.filter(
        pk__in=relationship_answerset_set.values_list('relationship',
                                                      flat=True))


def filter_people(form, at_date):
    answerset_set = models.PersonAnswerSet.objects.filter(
        Q(replaced_timestamp__gte=at_date)
        | Q(replaced_timestamp__isnull=True),
        timestamp__lte=at_date)

    # Filter answers to questions
    for field, values in form.cleaned_data.items():
        if field.startswith(f'{form.question_prefix}question_') and values:
            answerset_set = answerset_set.filter(question_answers__in=values)

    return models.Person.objects.filter(
        pk__in=answerset_set.values_list('person', flat=True))


def filter_organisations(form, at_date):
    answerset_set = models.OrganisationAnswerSet.objects.filter(
        Q(replaced_timestamp__gte=at_date)
        | Q(replaced_timestamp__isnull=True),
        timestamp__lte=at_date)

    # Filter answers to questions
    for field, values in form.cleaned_data.items():
        if field.startswith(f'{form.question_prefix}question_') and values:
            answerset_set = answerset_set.filter(question_answers__in=values)

    return models.Organisation.objects.filter(
        pk__in=answerset_set.values_list('organisation', flat=True))


class NetworkView(LoginRequiredMixin, TemplateView):
    """View to display relationship network."""
    template_name = 'people/network.html'

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if all(map(lambda f: f.is_valid(), forms.values())):
            return self.forms_valid(forms)

        return self.forms_invalid(forms)

    def get_forms(self):
        form_kwargs = self.get_form_kwargs()

        return {
            'relationship': forms.NetworkRelationshipFilterForm(**form_kwargs),
            'person': forms.NetworkPersonFilterForm(**form_kwargs),
            'organisation': forms.NetworkOrganisationFilterForm(**form_kwargs),
        }

    def get_form_kwargs(self):
        """Add GET params to form data."""
        kwargs = {}

        if self.request.method == 'GET':
            kwargs['data'] = self.request.GET

        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.request.POST

        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add filtered QuerySets of :class:`Person` and :class:`Relationship` to the context.
        """
        context = super().get_context_data(**kwargs)

        forms = self.get_forms()
        context['relationship_form'] = forms['relationship']
        context['person_form'] = forms['person']
        context['organisation_form'] = forms['organisation']

        if not all(map(lambda f: f.is_valid(), forms.values())):
            return context

        relationship_at_date = forms['relationship'].cleaned_data['date']
        if not relationship_at_date:
            relationship_at_date = timezone.now().date()

        person_at_date = forms['person'].cleaned_data['date']
        if not person_at_date:
            person_at_date = timezone.now().date()

        organisation_at_date = forms['organisation'].cleaned_data['date']
        if not organisation_at_date:
            organisation_at_date = timezone.now().date()

        # Filter on timestamp__date doesn't seem to work on MySQL
        # To compare datetimes we need at_date to be midnight at
        # the *end* of the day in question - so add one day here
        relationship_at_date += timezone.timedelta(days=1)

        context['person_set'] = serializers.PersonSerializer(
            filter_people(forms['person'], person_at_date),
            many=True).data

        context['organisation_set'] = serializers.OrganisationSerializer(
            filter_organisations(forms['organisation'], organisation_at_date),
            many=True).data

        context['relationship_set'] = serializers.RelationshipSerializer(
            filter_relationships(forms['relationship'], relationship_at_date),
            many=True).data

        logger.info('Found %d distinct relationships matching filters',
                    len(context['relationship_set']))

        return context

    def forms_valid(self, forms):
        try:
            return self.render_to_response(self.get_context_data())

        except ValidationError:
            return self.forms_invalid(forms)

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data())
