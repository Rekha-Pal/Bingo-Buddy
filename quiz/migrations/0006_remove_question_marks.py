# Generated by Django 3.0.5 on 2021-12-08 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_auto_20201209_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='marks',
        ),
    ]
