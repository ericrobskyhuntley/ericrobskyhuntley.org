# Generated by Django 2.1.7 on 2021-03-15 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_institution_postal'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='room',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
