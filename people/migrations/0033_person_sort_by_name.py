# Generated by Django 2.2.10 on 2021-02-08 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0032_personquestion_answer_is_public'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['name'], 'verbose_name_plural': 'people'},
        ),
    ]
