from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()  # pylint: disable=invalid-name


class ConsentForm(forms.ModelForm):
    """Form used to collect user consent for data collection / processing."""
    class Meta:
        model = User
        fields = ['consent_given']
        labels = {
            'consent_given':
            'I have read and understood this information and consent to my data being used in this way',
        }
