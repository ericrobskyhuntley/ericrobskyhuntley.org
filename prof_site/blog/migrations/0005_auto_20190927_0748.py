# Generated by Django 2.2 on 2019-09-27 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20190927_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='bib',
            field=models.FileField(blank=True, default='', upload_to='bibs/'),
            preserve_default=False,
        ),
    ]