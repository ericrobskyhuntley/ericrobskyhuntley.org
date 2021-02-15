# Generated by Django 2.2 on 2019-09-27 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_author_pronouns'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='orcid',
            field=models.CharField(blank=True, default='', max_length=19),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='author',
            name='pgp',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='author',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='authors/images/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='author',
            name='twitter',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
    ]