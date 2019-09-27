# Generated by Django 2.2 on 2019-09-27 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_author_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='pronouns',
            field=models.CharField(choices=[('M', 'He/him/his'), ('W', 'She/her/hers'), ('T', 'They/them/theirs')], default='T', max_length=1),
        ),
    ]