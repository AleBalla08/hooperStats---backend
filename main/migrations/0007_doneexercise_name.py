# Generated by Django 3.2.25 on 2025-06-11 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_doneexercise'),
    ]

    operations = [
        migrations.AddField(
            model_name='doneexercise',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
