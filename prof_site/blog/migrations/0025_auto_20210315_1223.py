# Generated by Django 2.1.7 on 2021-03-15 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_auto_20210315_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliation',
            name='end',
            field=models.DateField(blank=True, null=True),
        ),
    ]