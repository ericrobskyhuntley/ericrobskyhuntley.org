# Generated by Django 3.1.7 on 2021-03-22 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0051_auto_20210322_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='thesis_link',
            field=models.URLField(blank=True, default='', help_text='What is the website _connected to this affiliation_?'),
        ),
        migrations.AddField(
            model_name='education',
            name='thesis_title',
            field=models.CharField(blank=True, help_text='Major, concentration, etc.', max_length=300),
        ),
        migrations.AddField(
            model_name='education',
            name='thesis_type',
            field=models.CharField(blank=True, choices=[('diss', 'Dissertation'), ('mths', "Master's Thesis"), ('ugth', 'Undergraduate Thesis'), ('', 'None')], help_text='Major, concentration, etc.', max_length=4),
        ),
    ]
