# Generated by Django 2.2.9 on 2020-02-14 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_add_relationship_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name_plural': 'people'},
        ),
    ]
