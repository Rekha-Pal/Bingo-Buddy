# Generated by Django 3.0.5 on 2021-12-27 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='room_code',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
