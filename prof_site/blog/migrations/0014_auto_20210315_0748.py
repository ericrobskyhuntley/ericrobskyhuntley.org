# Generated by Django 2.1.7 on 2021-03-15 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_institution_website'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Author',
            new_name='Person',
        ),
    ]
