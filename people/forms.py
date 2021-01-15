"""Forms for creating / updating models belonging to the 'people' app."""

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


class OrganisationForm(forms.ModelForm):
    """Form for creating / updating an instance of :class:`Organisation`."""
    class Meta:
        model = models.Organisation
        fields = ['name', 'latitude', 'longitude']


class PersonForm(forms.ModelForm):
    """Form for creating / updating an instance of :class:`Person`."""
    class Meta:
        model = models.Person
        fields = [
            'name',
        ]


class RelationshipForm(forms.Form):
    target = forms.ModelChoiceField(
        models.Person.objects.all(),
        widget=ModelSelect2Widget(search_fields=['name__icontains']))


class DynamicAnswerSetBase(forms.Form):
    field_class = forms.ModelChoiceField
    field_widget = None
    field_required = True
    question_model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})

        for question in self.question_model.objects.all():
            field_class = self.field_class
            field_widget = self.field_widget

            if question.is_multiple_choice:
                field_class = forms.ModelMultipleChoiceField
                field_widget = Select2MultipleWidget

            field_name = f'question_{question.pk}'

            field = field_class(label=question,
                                queryset=question.answers,
                                widget=field_widget,
                                required=self.field_required,
                                initial=initial.get(field_name, None))
            self.fields[field_name] = field


class PersonAnswerSetForm(forms.ModelForm, DynamicAnswerSetBase):
    """Form for variable person attributes.

    Dynamic fields inspired by https://jacobian.org/2010/feb/28/dynamic-form-generation/
    """
    class Meta:
        model = models.PersonAnswerSet
        fields = [
            'nationality',
            'country_of_residence',
            'organisation',
            'organisation_started_date',
            'job_title',
            'disciplines',
            'themes',
            'latitude',
            'longitude',
        ]
        widgets = {
            'nationality': Select2Widget(),
            'country_of_residence': Select2Widget(),
            'themes': Select2MultipleWidget(),
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
        }
        help_texts = {
            'organisation_started_date':
            'If you don\'t know the exact date, an approximate date is okay.',
        }

    question_model = models.PersonQuestion

    def save(self, commit=True) -> models.PersonAnswerSet:
        # Save Relationship model
        self.instance = super().save(commit=False)
        self.instance.person_id = self.initial['person_id']
        if commit:
            self.instance.save()

        if commit:
            # Save answers to relationship questions
            for key, value in self.cleaned_data.items():
                if key.startswith('question_') and value:
                    try:
                        self.instance.question_answers.add(value)

                    except TypeError:
                        # Value is a QuerySet - multiple choice question
                        self.instance.question_answers.add(*value.all())

        return self.instance


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

    question_model = models.RelationshipQuestion

    def save(self, commit=True) -> models.RelationshipAnswerSet:
        # Save Relationship model
        self.instance = super().save(commit=commit)

        if commit:
            # Save answers to relationship questions
            for key, value in self.cleaned_data.items():
                if key.startswith('question_') and value:
                    try:
                        self.instance.question_answers.add(value)

                    except TypeError:
                        # Value is a QuerySet - multiple choice question
                        self.instance.question_answers.add(*value.all())

        return self.instance


class NetworkFilterForm(DynamicAnswerSetBase):
    """
    Form to provide filtering on the network view.
    """
    field_class = forms.ModelMultipleChoiceField
    field_widget = Select2MultipleWidget
    field_required = False
    question_model = models.RelationshipQuestion

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add date field to select relationships at a particular point in time
        self.fields['date'] = forms.DateField(
            required=False,
            widget=SelectDateWidget(years=get_date_year_range()),
            help_text='Show relationships as they were on this date')
