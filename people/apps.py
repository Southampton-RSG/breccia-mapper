import logging

from django.apps import AppConfig
from django.conf import settings
from django.core import serializers
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def load_welcome_template_fixture(fixture_path) -> bool:
    """Load welcome email template from a JSON fixture."""
    try:
        with open(fixture_path) as f:
            for deserialized in serializers.deserialize('json', f):
                if deserialized.object.name == settings.TEMPLATE_WELCOME_EMAIL_NAME:
                    deserialized.save()
                    logger.warning('Welcome email template \'%s\' loaded',
                                   deserialized.object.name)
                    return True

            return False

    except FileNotFoundError:
        logger.warning('Email template fixture not found.')
        return False


def send_welcome_email(sender, instance, created, **kwargs):
    from post_office import models

    if not created:
        # If user already exists, don't send welcome message
        return

    try:
        instance.send_welcome_email()

    except models.EmailTemplate.DoesNotExist:
        logger.warning(
            'Welcome email template \'%s\' not found - attempting to load from fixtures',
            settings.TEMPLATE_WELCOME_EMAIL_NAME)

        is_loaded = False
        if settings.CUSTOMISATION_NAME:
            # Customisation app present - try here first
            is_loaded |= load_welcome_template_fixture(
                settings.BASE_DIR.joinpath('custom', 'fixtures',
                                           'email_templates.json'))

        # |= operator shortcuts - only try here if we don't already have it
        is_loaded |= load_welcome_template_fixture(
            settings.BASE_DIR.joinpath('people', 'fixtures',
                                       'email_templates.json'))

        if is_loaded:
            instance.send_welcome_email()

        else:
            logger.error('Welcome email template \'%s\' not found',
                         settings.TEMPLATE_WELCOME_EMAIL_NAME)


class PeopleConfig(AppConfig):
    name = 'people'

    def ready(self) -> None:
        # Activate signal handlers
        post_save.connect(send_welcome_email, sender='people.user')
