# Generated by Django 5.2.1 on 2025-05-27 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='a_participe',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='participant',
            name='reponses',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
