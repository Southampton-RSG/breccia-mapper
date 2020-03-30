"""
Views belonging to the core of the project.

These views don't represent any of the models in the apps.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class ExportListView(LoginRequiredMixin, TemplateView):
    template_name = 'export.html'
