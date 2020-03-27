"""
Views for displaying or manipulating instances of :class:`Person`.
"""

from django.views.generic import CreateView, DetailView, ListView, UpdateView

from rest_framework.views import APIView, Response

from people import forms, models, permissions, serializers


class PersonCreateView(CreateView):
    """
    View to create a new instance of :class:`Person`.

    If 'user' is passed as a URL parameter - link the new person to the current user.
    """
    model = models.Person
    template_name = 'people/person/create.html'
    form_class = forms.PersonForm

    def form_valid(self, form):
        if 'user' in self.request.GET:
            form.instance.user = self.request.user

        return super().form_valid(form)


class PersonListView(ListView):
    """
    View displaying a list of :class:`Person` objects - searchable.
    """
    model = models.Person
    template_name = 'people/person/list.html'


class ProfileView(permissions.UserIsLinkedPersonMixin, DetailView):
    """
    View displaying the profile of a :class:`Person` - who may be a user.
    """
    model = models.Person
    template_name = 'people/person/detail.html'

    def get_object(self, queryset=None) -> models.Person:
        """
        Get the :class:`Person` object to be represented by this page.

        If not determined from url get current user.
        """
        try:
            return super().get_object(queryset)

        except AttributeError:
            # pk was not provided in URL
            return self.request.user.person


class PersonUpdateView(permissions.UserIsLinkedPersonMixin, UpdateView):
    """
    View for updating a :class:`Person` record.
    """
    model = models.Person
    template_name = 'people/person/update.html'
    form_class = forms.PersonForm


class PersonApiView(APIView):
    """
    List all :class:`Person` instances.
    """

    def get(self, request, format=None):
        """
        List all :class:`Person` instances.
        """
        serializer = serializers.PersonSerializer(models.Person.objects.all(),
                                                  many=True)
        return Response(serializer.data)
