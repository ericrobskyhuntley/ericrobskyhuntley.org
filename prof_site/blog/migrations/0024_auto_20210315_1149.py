# Generated by Django 2.1.7 on 2021-03-15 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0023_person_website'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='end',
            field=models.DateField(blank=True, null=True),
        ),
    ]
