"""Forms for creating / updating models belonging to the 'people' app."""

import typing

from django import forms
from django.conf import settings

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django_select2.forms import ModelSelect2Widget, Select2Widget, Select2MultipleWidget

from . import models


class OrganisationForm(forms.ModelForm):
    """Form for creating / updating an instance of :class:`Organisation`."""
    class Meta:
        model = models.Organisation
        fields = [
            'name',
        ]


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
    question_prefix: str = ''
    as_filters: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.negative_responses = {}
        field_order = []

        for question in self.question_model.objects.all():
            if self.as_filters and not question.answer_is_public:
                continue

            # Is a placeholder question just for sorting hardcoded questions?
            if (
                question.is_hardcoded
                and (self.as_filters or (question.hardcoded_field in self.Meta.fields))
            ):
                field_order.append(question.hardcoded_field)
                continue

            field_class = self.field_class
            field_widget = self.field_widget

            if question.is_multiple_choice:
                field_class = forms.ModelMultipleChoiceField
                field_widget = Select2MultipleWidget

            field_name = f'{self.question_prefix}question_{question.pk}'

            # If being used as a filter - do we have alternate text?
            field_label = question.text
            if self.as_filters and question.filter_text:
                field_label = question.filter_text

            field = field_class(
                label=field_label,
                queryset=question.answers,
                widget=field_widget,
                required=(self.field_required
                          and not question.allow_free_text),
                initial=self.initial.get(field_name, None),
                help_text=question.help_text if not self.as_filters else '')
            self.fields[field_name] = field
            field_order.append(field_name)

            try:
                negative_response = question.answers.get(is_negative_response=True)
                self.negative_responses[field_name] = negative_response.id
            
            except (self.answer_model.DoesNotExist, self.answer_model.MultipleObjectsReturned):
                pass

            if question.allow_free_text and not self.as_filters:
                free_field = forms.CharField(label=f'{question} free text',
                                             required=False)
                self.fields[f'{field_name}_free'] = free_field
                field_order.append(f'{field_name}_free')

        self.order_fields(field_order)


class OrganisationAnswerSetForm(forms.ModelForm, DynamicAnswerSetBase):
    """Form for variable organisation attributes.

    Dynamic fields inspired by https://jacobian.org/2010/feb/28/dynamic-form-generation/
    """
    class Meta:
        model = models.OrganisationAnswerSet
        fields = [
            'name',
            'website',
            'countries',
            'hq_country',
            'is_partner_organisation',
            'latitude',
            'longitude',
        ]
        labels = {
            'is_partner_organisation':
            f'Is this organisation a {settings.PARENT_PROJECT_NAME} partner organisation?'
        }
        widgets = {
            'countries': Select2MultipleWidget(),
            'hq_country': Select2Widget(),
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
        }

    question_model = models.OrganisationQuestion
    answer_model = models.OrganisationQuestionChoice

    def save(self, commit=True) -> models.OrganisationAnswerSet:
        # Save model
        self.instance = super().save(commit=False)
        self.instance.organisation_id = self.initial['organisation_id']
        if commit:
            self.instance.save()
            # Need to call same_m2m manually since we use commit=False above
            self.save_m2m()

        if commit:
            # Save answers to questions
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
            'project_started_date',
            'job_title',
            'disciplinary_background',
            'external_organisations',
            'latitude',
            'longitude',
        ]
        widgets = {
            'nationality': Select2MultipleWidget(),
            'country_of_residence': Select2Widget(),
            'organisation_started_date': DatePickerInput(),
            'project_started_date': DatePickerInput(),
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
        }
        labels = {
            'project_started_date':
            f'Date started on the {settings.PARENT_PROJECT_NAME} project',
            'external_organisations':
            'Please list the main organisations external to BRECcIA work that you have been working with since 1st January 2019 that are involved in food/water security in African dryland regions'
        }
        help_texts = {
            'organisation_started_date':
            'If you don\'t know the exact date, an approximate date is okay.',
            'project_started_date':
            'If you don\'t know the exact date, an approximate date is okay.',
        }

    question_model = models.PersonQuestion
    answer_model = models.PersonQuestionChoice

    def save(self, commit=True) -> models.PersonAnswerSet:
        # Save model
        self.instance = super().save(commit=False)
        self.instance.person_id = self.initial['person_id']
        if commit:
            self.instance.save()
            # Need to call same_m2m manually since we use commit=False above
            self.save_m2m()

        if commit:
            # Save answers to questions
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
        widgets = {
            'relationship': forms.HiddenInput,
        }

    question_model = models.RelationshipQuestion
    answer_model = models.RelationshipQuestionChoice

    def save(self, commit=True) -> models.RelationshipAnswerSet:
        # Save model
        self.instance = super().save(commit=commit)

        if commit:
            # Save answers to questions
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


class OrganisationRelationshipAnswerSetForm(forms.ModelForm,
                                            DynamicAnswerSetBase):
    """Form to allow users to describe a relationship with an organisation.

    Dynamic fields inspired by https://jacobian.org/2010/feb/28/dynamic-form-generation/
    """
    class Meta:
        model = models.OrganisationRelationshipAnswerSet
        fields = [
            'relationship',
        ]
        widgets = {
            'relationship': forms.HiddenInput,
        }

    question_model = models.OrganisationRelationshipQuestion
    answer_model = models.OrganisationRelationshipQuestionChoice

    def save(self, commit=True) -> models.OrganisationRelationshipAnswerSet:
        # Save model
        self.instance = super().save(commit=commit)

        if commit:
            # Save answers to questions
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


class DateForm(forms.Form):
    date = forms.DateField(
        required=False,
        widget=DatePickerInput(),
        help_text='Show relationships as they were on this date'
    )


class FilterForm(DynamicAnswerSetBase):
    """Filter objects by answerset responses."""
    field_class = forms.ModelMultipleChoiceField
    field_widget = Select2MultipleWidget
    field_required = False
    as_filters = True


class NetworkRelationshipFilterForm(FilterForm):
    """Filer relationships by answerset responses."""
    question_model = models.RelationshipQuestion
    answer_model = models.RelationshipQuestionChoice
    question_prefix = 'relationship_'


class NetworkPersonFilterForm(FilterForm):
    """Filer people by answerset responses."""
    question_model = models.PersonQuestion
    answer_model = models.PersonQuestionChoice
    question_prefix = 'person_'


class NetworkOrganisationFilterForm(FilterForm):
    """Filer organisations by answerset responses."""
    question_model = models.OrganisationQuestion
    answer_model = models.OrganisationQuestionChoice
    question_prefix = 'organisation_'
