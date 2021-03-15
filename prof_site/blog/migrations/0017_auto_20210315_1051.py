# Generated by Django 2.1.7 on 2021-03-15 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_department_lab_center_institution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='venue',
        ),
        migrations.AddField(
            model_name='event',
            name='host',
            field=models.ManyToManyField(blank=True, to='blog.Department_Lab_Center'),
        ),
    ]