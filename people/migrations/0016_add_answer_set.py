# Generated by Django 2.2.10 on 2020-03-04 12:09
import logging

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

logger = logging.getLogger(__name__)


def forward_migration(apps, schema_editor):
    """
    Move existing data forward into answer sets from the relationship.
    """
    Relationship = apps.get_model('people', 'Relationship')

    for relationship in Relationship.objects.all():
        answer_set = relationship.answer_sets.first()
        if answer_set is None:
            answer_set = relationship.answer_sets.create()

        for answer in relationship.question_answers.all():
            answer_set.question_answers.add(answer)

            
def backward_migration(apps, schema_editor):
    """
    Move data backward from answer sets onto the relationship.
    """
    Relationship = apps.get_model('people', 'Relationship')

    for relationship in Relationship.objects.all():
        answer_set = relationship.answer_sets.last()

        try:
            for answer in answer_set.question_answers.all():
                relationship.question_answers.add(answer)

        except AttributeError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0015_shrink_name_fields_to_255'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='relationship',
            name='expired',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='RelationshipAnswerSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('question_answers', models.ManyToManyField(to='people.RelationshipQuestionChoice')),
                ('relationship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_sets', to='people.Relationship')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.RunPython(forward_migration, backward_migration),
        migrations.RemoveField(
            model_name='relationship',
            name='question_answers',
        ),
    ]