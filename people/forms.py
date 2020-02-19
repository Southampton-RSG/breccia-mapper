"""
Forms for creating / updating models belonging to the 'people' app.
"""

from django import forms

from . import models


class PersonForm(forms.ModelForm):
    """
    Form for creating / updating an instance of :class:`Person`.
    """
    class Meta:
        model = models.Person
        fields = [
            'name',
            'core_member',
        ]
