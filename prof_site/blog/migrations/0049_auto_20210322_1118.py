# Generated by Django 3.1.7 on 2021-03-22 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0048_auto_20210322_1115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitewidesetting',
            name='main_bibliography',
        ),
        migrations.RemoveField(
            model_name='sitewidesetting',
            name='main_bibliography_collection',
        ),
        migrations.RemoveField(
            model_name='sitewidesetting',
            name='main_bibliography_file',
        ),
        migrations.RemoveField(
            model_name='sitewidesetting',
            name='main_bibliography_type',
        ),
        migrations.RemoveField(
            model_name='sitewidesetting',
            name='main_bibliography_version',
        ),
    ]