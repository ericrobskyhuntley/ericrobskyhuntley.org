# Generated by Django 2.1.7 on 2021-03-15 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0018_auto_20210315_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='postal',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]