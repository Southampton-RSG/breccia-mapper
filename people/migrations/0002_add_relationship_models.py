# Generated by Django 2.2.9 on 2020-01-30 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('core_member', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('text', models.CharField(max_length=1023)),
            ],
        ),
        migrations.CreateModel(
            name='RelationshipQuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1023)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='people.RelationshipQuestion')),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationships_as_source', to='people.Person')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationships_as_target', to='people.Person')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='relationship_targets',
            field=models.ManyToManyField(related_name='relationship_sources', through='people.Relationship', to='people.Person'),
        ),
        migrations.AddConstraint(
            model_name='relationshipquestionchoice',
            constraint=models.UniqueConstraint(fields=('question', 'text'), name='unique_question_answer'),
        ),
        migrations.AddConstraint(
            model_name='relationship',
            constraint=models.UniqueConstraint(fields=('source', 'target'), name='unique_relationship'),
        ),
    ]
