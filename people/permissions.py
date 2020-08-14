"""
Permission mixins for views relating to :class:`Person`s.
"""

from django.contrib.auth.mixins import UserPassesTestMixin

from . import models


class UserIsLinkedPersonMixin(UserPassesTestMixin):
    """
    Grant access if the user is staff or has a :class:`Person` record and
    this is the one referred to in the view.
    """
    related_person_field = None
    permission_denied_message = 'You do not have permission to view this page.'

    def get_test_person(self) -> models.Person:
        """
        Get the :class:`Person` to test the user against.
        """
        if self.related_person_field is None:
            test_person = self.get_object()

            if not isinstance(test_person, models.Person):
                raise AttributeError(
                    'View incorrectly configured: \'related_person_field\' must be defined.'
                )

            return test_person

        return getattr(self.get_object(), self.related_person_field)

    def test_func(self) -> bool:
        """
        Require that user is either staff or is the linked person.
        """
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff or self.get_test_person() == user.person)
