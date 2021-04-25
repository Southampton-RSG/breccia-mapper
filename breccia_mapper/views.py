"""Views belonging to the core of the project.

These views don't represent any of the models in the apps.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from . import forms

User = get_user_model()  # pylint: disable=invalid-name


class IndexView(TemplateView):
    # Template set in Django settings file - may be customised by a customisation app
    template_name = settings.TEMPLATE_NAME_INDEX


class ConsentTextView(LoginRequiredMixin, UpdateView):
    """View with consent text and form for users to indicate consent."""
    model = User
    form_class = forms.ConsentForm
    template_name = 'consent.html'

    def get_success_url(self) -> str:
        try:
            return reverse('people:person.detail', kwargs={'pk': self.request.user.person.pk})

        except AttributeError:
            return reverse('index')

    def get_object(self, *args, **kwargs) -> User:
        return self.request.user
