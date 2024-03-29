# Generated by Django 2.2.10 on 2020-02-19 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityMedium',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='medium',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='activities.ActivityMedium'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity',
            name='type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='activities.ActivityType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activityseries',
            name='medium',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='activities.ActivityMedium'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activityseries',
            name='type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='activities.ActivityType'),
            preserve_default=False,
        ),
    ]
