# Generated by Django 3.1.7 on 2021-03-18 22:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('blog', '0034_auto_20210318_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='post',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]