# Generated by Django 2.2.10 on 2021-02-15 13:54

import re

from django.db import migrations

from .utils.question_sets import port_question


def migrate_forward(apps, schema_editor):
    """Replace discipline text field with admin-editable question."""
    PersonAnswerSet = apps.get_model('people', 'PersonAnswerSet')

    discipline_question = port_question(apps,
                                        'Disciplines', [],
                                        is_multiple_choice=True,
                                        allow_free_text=True)

    for answerset in PersonAnswerSet.objects.all():
        try:
            disciplines = [
                d.strip() for d in re.split(r'[,;]+', answerset.disciplines)
            ]

        except TypeError:
            continue

        for discipline in disciplines:
            answer, _ = discipline_question.answers.get_or_create(
                text=discipline)
            answerset.question_answers.add(answer)


def migrate_backward(apps, schema_editor):
    """Replace discipline admin-editable question with text field."""
    PersonAnswerSet = apps.get_model('people', 'PersonAnswerSet')
    PersonQuestion = apps.get_model('people', 'PersonQuestion')

    discipline_question = PersonQuestion.objects.filter(
        text='Disciplines').latest('version')

    for answerset in PersonAnswerSet.objects.all():
        answerset.disciplines = ', '.join(
            answerset.question_answers.filter(
                question=discipline_question).values_list('text', flat=True))
        answerset.save()

    PersonQuestion.objects.filter(text='Disciplines').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0033_person_sort_by_name'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
        migrations.RemoveField(
            model_name='personanswerset',
            name='disciplines',
        ),
    ]
