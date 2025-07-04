# Generated by Django 5.1.6 on 2025-02-07 08:02

import buddyTracker.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddyTracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='breed',
            field=models.CharField(help_text='Enter the breed of the pet', max_length=50, verbose_name='Breed'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='id',
            field=models.CharField(default=buddyTracker.models.generate_uid, editable=False, max_length=6, primary_key=True, serialize=False, unique=True),
        ),
    ]
