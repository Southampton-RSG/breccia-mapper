"""
Views for displaying networks of :class:`People` and :class:`Relationship`s.
"""

import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.forms import ValidationError
from django.utils import timezone
from django.views.generic import TemplateView

from people import forms, models, serializers

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def filter_by_form_answers(queryset: QuerySet, answerset_queryset: QuerySet, relationship_key: str):
    """Build a filter to select based on form responses."""
    def inner(form):
        # Filter on timestamp__date doesn't seem to work on MySQL
        # To compare datetimes we need at_date to be midnight at
        # the *end* of the day in question - so add one day

        at_date = form.cleaned_data['date']
        if not at_date:
            at_date = timezone.now().date()
        at_date += timezone.timedelta(days=1)

        # Filter to answersets valid at required time
        answerset_set = answerset_queryset.prefetch_related('question_answers').filter(
            Q(replaced_timestamp__gte=at_date)
            | Q(replaced_timestamp__isnull=True),
            timestamp__lte=at_date
        )

        # Filter to answersets containing required answers
        for field, values in form.cleaned_data.items():
            if field.startswith(f'{form.question_prefix}question_') and values:
                answerset_set = answerset_set.filter(question_answers__in=values)

        return queryset.filter(pk__in=answerset_set.values_list(relationship_key, flat=True))

    return inner


filter_relationships = filter_by_form_answers(
    models.Relationship.objects.prefetch_related('source', 'target'),
    models.RelationshipAnswerSet.objects, 'relationship'
)

filter_organisations = filter_by_form_answers(
    models.Organisation.objects, models.OrganisationAnswerSet.objects, 'organisation'
)

filter_people = filter_by_form_answers(
    models.Person.objects, models.PersonAnswerSet.objects, 'person'
)


class NetworkView(LoginRequiredMixin, TemplateView):
    """View to display relationship network."""
    template_name = 'people/network.html'

    def post(self, request, *args, **kwargs):
        all_forms = self.get_forms()
        if all(map(lambda f: f.is_valid(), all_forms.values())):
            return self.forms_valid(all_forms)

        return self.forms_invalid(all_forms)

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

        all_forms = self.get_forms()
        context['relationship_form'] = all_forms['relationship']
        context['person_form'] = all_forms['person']
        context['organisation_form'] = all_forms['organisation']

        if not all(map(lambda f: f.is_valid(), all_forms.values())):
            return context

        context['person_set'] = serializers.PersonSerializer(
            filter_people(all_forms['person']), many=True
        ).data

        context['organisation_set'] = serializers.OrganisationSerializer(
            filter_organisations(all_forms['organisation']), many=True
        ).data

        context['relationship_set'] = serializers.RelationshipSerializer(
            filter_relationships(all_forms['relationship']), many=True
        ).data

        context['organisation_relationship_set'] = serializers.OrganisationRelationshipSerializer(
            models.OrganisationRelationship.objects.prefetch_related('source', 'target').all(),
            many=True
        ).data

        for person in models.Person.objects.all():
            try:
                context['organisation_relationship_set'].append(
                    {
                        'pk': f'membership-{person.pk}',
                        'source': serializers.PersonSerializer(person).data,
                        'target': serializers.OrganisationSerializer(
                            person.current_answers.organisation
                        ).data,
                        'kind': 'organisation-membership'
                    }
                )

            except AttributeError:
                pass

        logger.info(
            'Found %d distinct relationships matching filters', len(context['relationship_set'])
        )

        return context

    def forms_valid(self, all_forms):
        try:
            return self.render_to_response(self.get_context_data())

        except ValidationError:
            return self.forms_invalid(all_forms)

    def forms_invalid(self, all_forms):
        return self.render_to_response(self.get_context_data())
