"""
Views for displaying / manipulating models within the Activities app.
"""
from django.views.generic import DetailView, ListView

from . import models


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
