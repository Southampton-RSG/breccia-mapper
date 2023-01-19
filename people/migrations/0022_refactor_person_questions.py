# Generated by Django 2.2.10 on 2020-11-23 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0021_refactor_person_disciplines'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('text', models.CharField(max_length=255)),
                ('order', models.SmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'text'],
            },
        ),
        migrations.CreateModel(
            name='PersonQuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('order', models.SmallIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='people.PersonQuestion')),
            ],
            options={
                'ordering': ['question__order', 'order', 'text'],
            },
        ),
        migrations.CreateModel(
            name='PersonAnswerSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('replaced_timestamp', models.DateTimeField(blank=True, editable=False, null=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_sets', to='people.Person')),
                ('question_answers', models.ManyToManyField(to='people.PersonQuestionChoice')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.AddConstraint(
            model_name='personquestionchoice',
            constraint=models.UniqueConstraint(fields=('question', 'text'), name='unique_question_answer_personquestionchoice'),
        ),
    ]
