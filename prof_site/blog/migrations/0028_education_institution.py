# Generated by Django 2.1.7 on 2021-03-15 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_auto_20210315_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='institution',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='blog.Institution'),
            preserve_default=False,
        ),
    ]