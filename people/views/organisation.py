import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from people import forms, models


class OrganisationCreateView(LoginRequiredMixin, CreateView):
    """View to create a new instance of :class:`Organisation`."""
    model = models.Organisation
    template_name = 'people/organisation/create.html'
    form_class = forms.OrganisationForm


def try_copy_by_key(src_dict: typing.Mapping[str, typing.Any],
                    dest_dict: typing.MutableMapping[str, typing.Any],
                    key: str) -> None:
    """Copy a value by key from one dictionary to another.

    If the key does not exist, skip it.
    """
    value = src_dict.get(key, None)
    if value is not None:
        dest_dict[key] = value


class OrganisationListView(LoginRequiredMixin, ListView):
    """View displaying a list of :class:`organisation` objects."""
    model = models.Organisation
    template_name = 'people/organisation/list.html'

    @staticmethod
    def sort_organisation_countries(
        orgs_by_country: typing.MutableMapping[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """Sort dictionary of organisations by country.

        Sort order:
        - Project partners
        - International organisations
        - Organisations by country alphabetically
        - Organisations with unknown country
        """
        orgs_sorted = {}

        try_copy_by_key(orgs_by_country, orgs_sorted,
                        f'{settings.PARENT_PROJECT_NAME} partners')
        try_copy_by_key(orgs_by_country, orgs_sorted, 'International')

        special = {
            f'{settings.PARENT_PROJECT_NAME} partners', 'International',
            'Unknown'
        }
        for country in sorted(k for k in orgs_by_country.keys()
                              if k not in special):
            orgs_sorted[country] = orgs_by_country[country]

        try_copy_by_key(orgs_by_country, orgs_sorted, 'Unknown')

        return orgs_sorted

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)

        orgs_by_country = {}
        for organisation in self.get_queryset().all():
            answers = organisation.current_answers

            country = 'Unknown'
            try:
                if len(answers.countries) == 1:
                    country = answers.countries[0].name

                elif len(answers.countries) > 1:
                    country = 'International'

                if answers.is_partner_organisation:
                    country = f'{settings.PARENT_PROJECT_NAME} partners'

            except AttributeError:
                # Organisation has no AnswerSet - country is 'Unknown'
                pass

            orgs = orgs_by_country.get(country, [])
            orgs.append(organisation)
            orgs_by_country[country] = orgs

        # Sort into meaningful order
        context['orgs_by_country'] = self.sort_organisation_countries(
            orgs_by_country)

        context['existing_relationships'] = set(
            self.request.user.person.organisation_relationship_targets.
            values_list('pk', flat=True))

        return context


class OrganisationDetailView(LoginRequiredMixin, DetailView):
    """View displaying details of a :class:`Organisation`."""
    model = models.Organisation
    context_object_name = 'organisation'
    template_name = 'people/organisation/detail.html'

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Add map marker to context."""
        context = super().get_context_data(**kwargs)

        answerset = self.object.current_answers
        context['answer_set'] = answerset
        context['map_markers'] = [{
            'name': self.object.name,
            'lat': getattr(answerset, 'latitude', None),
            'lng': getattr(answerset, 'longitude', None),
        }]

        return context


class OrganisationUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a :class:`Organisation` record."""
    model = models.Organisation
    context_object_name = 'organisation'
    template_name = 'people/organisation/update.html'
    form_class = forms.OrganisationAnswerSetForm

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """Add map marker to context."""
        context = super().get_context_data(**kwargs)

        answerset = self.object.current_answers
        context['map_markers'] = [{
            'name': self.object.name,
            'lat': getattr(answerset, 'latitude', None),
            'lng': getattr(answerset, 'longitude', None),
        }]

        return context

    def get_initial(self) -> typing.Dict[str, typing.Any]:
        try:
            previous_answers = self.object.current_answers.as_dict()

        except AttributeError:
            previous_answers = {}

        previous_answers.update({
            'organisation_id': self.object.id,
        })

        return previous_answers

    def get_form_kwargs(self) -> typing.Dict[str, typing.Any]:
        """Remove instance from form kwargs as it's an Organisation, but expects an OrganisationAnswerSet."""
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')

        return kwargs

    def form_valid(self, form):
        """Mark any previous answer sets as replaced."""
        response = super().form_valid(form)
        now_date = timezone.now().date()

        # Saving the form made self.object an OrganisationAnswerSet - so go up, then back down
        # Shouldn't be more than one after initial updates after migration
        for answer_set in self.object.organisation.answer_sets.exclude(
                pk=self.object.pk):
            answer_set.replaced_timestamp = now_date
            answer_set.save()

        return response
