# Generated by Django 2.2.10 on 2020-02-20 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_relationship_questions_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='question_answers',
            field=models.ManyToManyField(to='people.RelationshipQuestionChoice'),
        ),
    ]