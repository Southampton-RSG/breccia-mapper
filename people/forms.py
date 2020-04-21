"""
Forms for creating / updating models belonging to the 'people' app.
"""
from django import forms

from django_select2.forms import Select2Widget, Select2MultipleWidget

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
            'gender',
            'age_group',
            'nationality',
            'country_of_residence',
            'organisation',
            'job_title',
            'discipline',
            'role',
            'themes',
        ]
        widgets = {
            'nationality': Select2Widget(),
            'country_of_residence': Select2Widget(),
            'themes': Select2MultipleWidget(),
        }
        
        
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
        self.fields['date'] = forms.DateField(required=False)
