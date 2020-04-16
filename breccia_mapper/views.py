"""
Views belonging to the core of the project.

These views don't represent any of the models in the apps.
"""

from django.conf import settings
from django.views.generic import TemplateView


class IndexView(TemplateView):
    # Template set in Django settings file - may be customised by a customisation app
    template_name = settings.TEMPLATE_NAME_INDEX
