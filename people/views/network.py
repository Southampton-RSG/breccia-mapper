"""
Views for displaying networks of :class:`People` and :class:`Relationship`s.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
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
        form = context['form']

        at_time = timezone.now()

        relationship_set = models.Relationship.objects.all()

        # Filter answers to relationship questions
        for key, value in form.data.items():
            if key.startswith('question_') and value:
                question_id = key.replace('question_', '', 1)
                answer = models.RelationshipQuestionChoice.objects.get(pk=value,
                                                                       question__pk=question_id)
                relationship_set = relationship_set.filter(
                    Q(answer_sets__replaced_timestamp__gt=at_time) | Q(answer_sets__replaced_timestamp__isnull=True),
                    answer_sets__timestamp__lte=at_time,
                    answer_sets__question_answers=answer
                )

        context['person_set'] = serializers.PersonSerializer(
            models.Person.objects.all(),
            many=True
        ).data

        context['relationship_set'] = serializers.RelationshipSerializer(
            relationship_set,
            many=True
        ).data

        return context

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data())
