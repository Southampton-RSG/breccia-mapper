"""Forms for creating / updating models belonging to the 'people' app."""

import typing

from django import forms

from bootstrap_datepicker_plus import DatePickerInput
from django_select2.forms import ModelSelect2Widget, Select2Widget, Select2MultipleWidget

from . import models


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
    field_required = True
    field_widget: typing.Optional[typing.Type[forms.Widget]] = None
    question_model: typing.Type[models.Question]
    answer_model: typing.Type[models.QuestionChoice]

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

            if question.allow_free_text:
                free_field = forms.CharField(label=f'{question} free text',
                                             required=False)
                self.fields[f'{field_name}_free'] = free_field


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
            'themes',
            'latitude',
            'longitude',
        ]
        widgets = {
            'nationality': Select2Widget(),
            'country_of_residence': Select2Widget(),
            'organisation_started_date': DatePickerInput(format='%Y-%m-%d'),
            'themes': Select2MultipleWidget(),
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
        }
        help_texts = {
            'organisation_started_date':
            'If you don\'t know the exact date, an approximate date is okay.',
        }

    question_model = models.PersonQuestion
    answer_model = models.PersonQuestionChoice

    def save(self, commit=True) -> models.PersonAnswerSet:
        # Save Relationship model
        self.instance = super().save(commit=False)
        self.instance.person_id = self.initial['person_id']
        if commit:
            self.instance.save()
            # Need to call same_m2m manually since we use commit=False above
            self.save_m2m()

        if commit:
            # Save answers to relationship questions
            for key, value in self.cleaned_data.items():
                if key.startswith('question_') and value:
                    if key.endswith('_free'):
                        # Create new answer from free text
                        value, _ = self.answer_model.objects.get_or_create(
                            text=value,
                            question=self.question_model.objects.get(
                                pk=key.split('_')[1]))

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
    answer_model = models.RelationshipQuestionChoice

    def save(self, commit=True) -> models.RelationshipAnswerSet:
        # Save Relationship model
        self.instance = super().save(commit=commit)

        if commit:
            # Save answers to relationship questions
            for key, value in self.cleaned_data.items():
                if key.startswith('question_') and value:
                    if key.endswith('_free'):
                        # Create new answer from free text
                        value, _ = self.answer_model.objects.get_or_create(
                            text=value,
                            question=self.question_model.objects.get(
                                pk=key.split('_')[1]))

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
    answer_model = models.RelationshipQuestionChoice

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add date field to select relationships at a particular point in time
        self.fields['date'] = forms.DateField(
            required=False,
            widget=DatePickerInput(format='%Y-%m-%d'),
            help_text='Show relationships as they were on this date')
