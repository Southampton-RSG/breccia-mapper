import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from people import forms, models, permissions
from breccia_mapper.views import UserIsStaffMixin


def get_map_data(obj: typing.Union[models.Person, models.Organisation]) -> typing.Dict[str, typing.Any]:
    """Prepare data to mark people or organisations on a map."""
    answer_set = obj.current_answers
    organisation = getattr(answer_set, 'organisation', None)

    try:
        country = answer_set.country_of_residence.name

    except AttributeError:
        country = None

    return {
        'name': obj.name,
        'lat': getattr(answer_set, 'latitude', None),
        'lng': getattr(answer_set, 'longitude', None),
        'organisation': getattr(organisation, 'name', None),
        'org_lat': getattr(organisation, 'latitude', None),
        'org_lng': getattr(organisation, 'longitude', None),
        'country': country,
        'url': obj.get_absolute_url(),
        'type': type(obj).__name__,
    }


class MapView(UserIsStaffMixin, LoginRequiredMixin, TemplateView):
    """View displaying a map of :class:`Person` and :class:`Organisation` locations."""
    template_name = 'people/map.html'

    def get_context_data(self,
                         **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)

        map_markers = []

        map_markers.extend(
            get_map_data(person) for person in models.Person.objects.all())
        map_markers.extend(
            get_map_data(org) for org in models.Organisation.objects.all())
        context['map_markers'] = map_markers

        return context
