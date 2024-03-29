# Generated by Django 2.2.10 on 2021-03-19 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0048_disciplines_and_organisations'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organisationanswerset',
            options={'get_latest_by': 'timestamp', 'ordering': ['timestamp']},
        ),
        migrations.AlterModelOptions(
            name='organisationrelationship',
            options={'get_latest_by': 'created'},
        ),
        migrations.AlterModelOptions(
            name='organisationrelationshipanswerset',
            options={'get_latest_by': 'timestamp', 'ordering': ['timestamp']},
        ),
        migrations.AlterModelOptions(
            name='personanswerset',
            options={'get_latest_by': 'timestamp', 'ordering': ['timestamp']},
        ),
        migrations.AlterModelOptions(
            name='relationship',
            options={'get_latest_by': 'created'},
        ),
        migrations.AlterModelOptions(
            name='relationshipanswerset',
            options={'get_latest_by': 'timestamp', 'ordering': ['timestamp']},
        ),
    ]
