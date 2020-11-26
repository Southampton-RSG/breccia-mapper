"""
Forms for creating / updating models belonging to the 'people' app.
"""

import typing

from django import forms
from django.forms.widgets import SelectDateWidget
from django.utils import timezone

from django_select2.forms import ModelSelect2Widget, Select2Widget, Select2MultipleWidget

from . import models


def get_date_year_range() -> typing.Iterable[int]:
    """
    Get sensible year range for SelectDateWidgets in the past.

    By default these widgets show 10 years in the future.
    """
    num_years_display = 60
    this_year = timezone.datetime.now().year
    return range(this_year, this_year - num_years_display, -1)


class PersonForm(forms.ModelForm):
    """
    Form for creating / updating an instance of :class:`Person`.
    """
    class Meta:
        model = models.Person
        fields = [
            'name',
            'gender',
            'age_group',
            'nationality',
            'country_of_residence',
            'organisation',
            'organisation_started_date',
            'job_title',
            'disciplines',
            'themes',
        ]
        widgets = {
            'nationality': Select2Widget(),
            'country_of_residence': Select2Widget(),
            'themes': Select2MultipleWidget(),
        }
        help_texts = {
            'organisation_started_date':
            'If you don\'t know the exact date, an approximate date is okay.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['organisation_started_date'].widget = SelectDateWidget(
            years=get_date_year_range())


class RelationshipForm(forms.Form):
    target = forms.ModelChoiceField(
        models.Person.objects.all(),
        widget=ModelSelect2Widget(search_fields=['name__icontains']))


class DynamicAnswerSetBase(forms.Form):
    field_class = forms.ModelChoiceField
    field_widget = None
    field_required = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for question in models.RelationshipQuestion.objects.all():
            field = self.field_class(label=question,
                                     queryset=question.answers,
                                     widget=self.field_widget,
                                     required=self.field_required)
            self.fields['question_{}'.format(question.pk)] = field


class RelationshipAnswerSetForm(forms.ModelForm, DynamicAnswerSetBase):
    """
    Form to allow users to describe a relationship.

    Dynamic fields inspired by https://jacobian.org/2010/feb/28/dynamic-form-generation/
    """
    class Meta:
        model = models.RelationshipAnswerSet
        fields = [
            'relationship',
        ]

    def save(self, commit=True) -> models.RelationshipAnswerSet:
        # Save Relationship model
        self.instance = super().save(commit=commit)

        if commit:
            # Save answers to relationship questions
            for key, value in self.cleaned_data.items():
                if key.startswith('question_') and value:
                    self.instance.question_answers.add(value)

        return self.instance


class NetworkFilterForm(DynamicAnswerSetBase):
    """
    Form to provide filtering on the network view.
    """
    field_class = forms.ModelMultipleChoiceField
    field_widget = Select2MultipleWidget
    field_required = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add date field to select relationships at a particular point in time
        self.fields['date'] = forms.DateField(
            required=False,
            widget=SelectDateWidget(years=get_date_year_range()),
            help_text='Show relationships as they were on this date')
