# Generated by Django 3.1.7 on 2021-03-19 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0040_auto_20210319_1449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='display_date',
            new_name='display_datetime',
        ),
    ]
