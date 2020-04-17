"""
Views for displaying networks of :class:`People` and :class:`Relationship`s.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import ValidationError
from django.utils import timezone
from django.views.generic import FormView


from people import forms, models, serializers


class NetworkView(LoginRequiredMixin, FormView):
    """
    View to display relationship network.
    """
    template_name = 'people/network.html'
    form_class = forms.NetworkFilterForm

    def get_form_kwargs(self):
        """
        Add GET params to form data.
        """
        kwargs = super().get_form_kwargs()

        if self.request.method == 'GET':
            if 'data' in kwargs:
                kwargs['data'].update(self.request.GET)

            else:
                kwargs['data'] = self.request.GET

        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add filtered QuerySets of :class:`Person` and :class:`Relationship` to the context.
        """
        context = super().get_context_data(**kwargs)
        form: forms.NetworkFilterForm = context['form']
        if not form.is_valid():
            raise ValidationError

        at_time = timezone.now()

        relationship_set = models.Relationship.objects.all()

        # Filter answers to relationship questions
        for field, values in form.cleaned_data.items():
            if field.startswith('question_') and values:
                relationship_set = relationship_set.filter(
                    # Time filters must be here
                    Q(answer_sets__replaced_timestamp__gt=at_time) | Q(answer_sets__replaced_timestamp__isnull=True),
                    answer_sets__timestamp__lte=at_time,
                    answer_sets__question_answers__in=values
                )

        context['person_set'] = serializers.PersonSerializer(
            models.Person.objects.all(),
            many=True
        ).data

        context['relationship_set'] = serializers.RelationshipSerializer(
            relationship_set.distinct(),
            many=True
        ).data

        return context

    def form_valid(self, form):
        try:
            return self.render_to_response(self.get_context_data())
        
        except ValidationError:
            return self.form_invalid(form)
