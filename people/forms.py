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
        exclude = [
            'user',
            'relationship_targets',
        ]
        widgets = {
            'nationality': Select2Widget(),
            'country_of_residence': Select2Widget(),
            'themes': Select2MultipleWidget(),
        }


class RelationshipForm(forms.ModelForm):
    """
    Form to allow users to describe a relationship - includes :class:`RelationshipQuestion`s.

    Dynamic fields inspired by https://jacobian.org/2010/feb/28/dynamic-form-generation/
    """
    class Meta:
        model = models.Relationship
        fields = [
            'source',
            'target',
        ]
        widgets = {
            'source': Select2Widget(),
            'target': Select2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for question in models.RelationshipQuestion.objects.all():
            # Get choices from model and add default 'not selected' option
            choices = question.choices + [['', '---------']]

            field = forms.ChoiceField(label=question,
                                      choices=choices)
            self.fields['question_{}'.format(question.pk)] = field

    def save(self, commit=True) -> models.Relationship:
        # Save Relationship model
        self.instance = super().save(commit=commit)

        if commit:
            # Save answers to relationship questions
            for key, value in self.cleaned_data.items():
                if key.startswith('question_'):
                    answer = models.RelationshipQuestionChoice.objects.get(pk=value)
                    self.instance.question_answers.add(answer)

        return self.instance
