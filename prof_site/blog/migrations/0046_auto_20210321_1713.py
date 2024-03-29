# Generated by Django 3.1.7 on 2021-03-21 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0045_auto_20210321_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitewidesetting',
            name='main_bibliography_file',
            field=models.FileField(blank=True, default='', help_text='Bibliography file. Formatted in BetterBibLaTex.', upload_to=''),
        ),
        migrations.AddField(
            model_name='sitewidesetting',
            name='main_bibliography_version',
            field=models.IntegerField(blank=True, help_text='Which person is the focus of this site?', null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='attach_kind',
            field=models.CharField(blank=True, default='', help_text='What kind of thing is the attachment? E.g., syllabus, article).', max_length=150, null=True),
        ),
    ]
