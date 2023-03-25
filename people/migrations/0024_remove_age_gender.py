# Generated by Django 2.2.10 on 2020-11-26 13:03

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations

from backports.db.models.enums import TextChoices
from .utils.question_sets import port_question


class GenderChoices(TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    NON_BINARY = 'B', 'Non-binary'
    OTHER = 'O', 'Other'
    PREFER_NOT_TO_SAY = 'N', 'Prefer not to say'


class AgeGroupChoices(TextChoices):
    LTE_25 = '<=25', '25 or under'
    BETWEEN_26_30 = '26-30', '26-30'
    BETWEEN_31_35 = '31-35', '31-35'
    BETWEEN_36_40 = '36-40', '36-40'
    BETWEEN_41_45 = '41-45', '41-45'
    BETWEEN_46_50 = '46-50', '46-50'
    BETWEEN_51_55 = '51-55', '51-55'
    BETWEEN_56_60 = '56-60', '56-60'
    GTE_61 = '>=61', '61 or older'
    PREFER_NOT_TO_SAY = 'N', 'Prefer not to say'


def migrate_forward(apps, schema_editor):
    Person = apps.get_model('people', 'Person')

    gender_question = port_question(apps, 'Gender', GenderChoices.labels)
    age_question = port_question(apps, 'Age', AgeGroupChoices.labels)

    for person in Person.objects.all():
        try:
            answer_set = person.answer_sets.latest('timestamp')

        except ObjectDoesNotExist:
            answer_set = person.answer_sets.create()

        try:
            gender = [
                item for item in GenderChoices if item.value == person.gender
            ][0]
            answer_set.question_answers.filter(
                question__text=gender_question.text).delete()
            answer_set.question_answers.add(
                gender_question.answers.get(text__iexact=gender.label))

        except (AttributeError, IndexError):
            pass

        try:
            age = [
                item for item in AgeGroupChoices
                if item.value == person.age_group
            ][0]
            answer_set.question_answers.filter(
                question__text=age_question.text).delete()
            answer_set.question_answers.add(
                age_question.answers.get(text__iexact=age.label))

        except (AttributeError, IndexError):
            pass


def migrate_backward(apps, schema_editor):
    Person = apps.get_model('people', 'Person')

    for person in Person.objects.all():
        try:
            current_answers = person.answer_sets.latest('timestamp')
            age_answer = current_answers.question_answers.get(
                question__text='Age')

            person.age_group = [
                item for item in AgeGroupChoices
                if item.label == age_answer.text
            ][0].value

            person.save()

        except ObjectDoesNotExist:
            pass

        try:
            current_answers = person.answer_sets.latest('timestamp')
            gender_answer = current_answers.question_answers.get(
                question__text='Gender')
            person.gender = [

                item for item in GenderChoices
                if item.label == gender_answer.text
            ][0].value

            person.save()

        except ObjectDoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0023_remove_person_role'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
        migrations.RemoveField(
            model_name='person',
            name='age_group',
        ),
        migrations.RemoveField(
            model_name='person',
            name='gender',
        ),
    ]
