"""
Views for displaying / manipulating models within the Activities app.
"""
import json

from django.http import HttpResponse
from django.views.generic import DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from people import models as people_models
from people import permissions
from . import models


class ActivitySeriesListView(ListView):
    """
    View displaying a list of :class:`ActivitySeries`.
    """
    model = models.ActivitySeries
    template_name = 'activities/activity_series/list.html'
    context_object_name = 'activity_series_list'


class ActivitySeriesDetailView(DetailView):
    """
    View displaying details of a single :class:`ActivitySeries`.
    """
    model = models.ActivitySeries
    template_name = 'activities/activity_series/detail.html'
    context_object_name = 'activity_series'


class ActivityListView(ListView):
    """
    View displaying a list of :class:`Activity`.
    """
    model = models.Activity
    template_name = 'activities/activity/list.html'


class ActivityDetailView(DetailView):
    """
    View displaying details of a single :class:`Activity`.
    """
    model = models.Activity
    template_name = 'activities/activity/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_is_attending'] = self.object.attendance_list.filter(
            pk=self.request.user.person.pk
        ).exists()

        return context


class ActivityAttendanceView(permissions.UserIsLinkedPersonMixin, SingleObjectMixin, View):
    """
    View to add or delete attendance of an activity.
    """
    model = models.Activity

    def get_test_person(self) -> people_models.Person:
        data = json.loads(self.request.body)

        self.person = people_models.Person.objects.get(pk=data['pk'])
        return self.person

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.is_ajax():
            self.object.attendance_list.add(self.person)

            return HttpResponse(status=204)

        return HttpResponse("URL does not support non-AJAX requests", status=400)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.is_ajax():
            self.object.attendance_list.remove(self.person)

            return HttpResponse(status=204)

        return HttpResponse("URL does not support non-AJAX requests", status=400)
