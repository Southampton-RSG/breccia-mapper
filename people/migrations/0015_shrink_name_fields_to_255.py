# Generated by Django 2.2.10 on 2020-02-28 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0014_person_role_themes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationshipquestion',
            name='text',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='relationshipquestionchoice',
            name='text',
            field=models.CharField(max_length=255),
        ),
    ]