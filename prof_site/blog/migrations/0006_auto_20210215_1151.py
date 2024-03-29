# Generated by Django 2.1.7 on 2021-02-15 16:51

from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190927_0748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliation',
            name='website',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='author',
            name='desc',
            field=markdownx.models.MarkdownxField(blank=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='dpt',
            field=models.CharField(blank=True, default='', max_length=150),
            preserve_default=False,
        ),
    ]
