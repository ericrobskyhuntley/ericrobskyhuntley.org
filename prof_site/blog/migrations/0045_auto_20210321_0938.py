# Generated by Django 3.1.7 on 2021-03-21 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0044_sitewidesetting_main_bibliography_collection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='attach_kind',
            field=models.CharField(blank=True, default='', help_text='What kind of thing is the attachment? E.g., syllabus, article).', max_length=150),
        ),
    ]
