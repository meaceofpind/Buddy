# Generated by Django 5.1.6 on 2025-02-07 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Enter the pet's name", max_length=100, verbose_name='Pet Name')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], help_text="Select the pet's gender", max_length=1, verbose_name='Pet Gender')),
                ('age', models.PositiveIntegerField(help_text="Enter the pet's age in years", verbose_name='Pet Age')),
                ('species', models.CharField(choices=[('Dog', 'Dog'), ('Cat', 'Cat')], help_text='Enter the species of the pet', max_length=50, verbose_name='Species')),
                ('breed', models.CharField(choices=[('Dog', 'Dog'), ('Cat', 'Cat')], help_text='Enter the breed of the pet', max_length=50, verbose_name='Breed')),
                ('last_modified', models.DateTimeField(auto_now=True, help_text='The date and time when this record was last modified', verbose_name='Last Modified')),
            ],
        ),
        migrations.CreateModel(
            name='TrackerEntries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pet_entries', to='buddyTracker.pet')),
            ],
        ),
        migrations.CreateModel(
            name='TrackerEntryData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=100, verbose_name='Field Name')),
                ('field_type', models.CharField(max_length=50, verbose_name='Field Type')),
                ('field_value', models.JSONField(help_text='Store the value in appropriate data type', verbose_name='Field Value (Dynamic)')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='buddyTracker.trackerentries', verbose_name='Entry')),
            ],
        ),
        migrations.CreateModel(
            name='TrackerList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the name of the tracker (e.g., Vaccination, Treatment)', max_length=100, verbose_name='Tracker Name')),
                ('pet', models.ForeignKey(help_text='Select the pet associated with this tracker', on_delete=django.db.models.deletion.CASCADE, related_name='tracker_lists', to='buddyTracker.pet', verbose_name='Pet')),
            ],
        ),
        migrations.AddField(
            model_name='trackerentries',
            name='tracker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='buddyTracker.trackerlist'),
        ),
        migrations.CreateModel(
            name='FormOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(help_text='Enter the field name (e.g., Vaccination Date, Treatment Cost)', max_length=100, verbose_name='Field Name')),
                ('field_type', models.CharField(choices=[('CharField', 'Text'), ('DateField', 'Date'), ('FloatField', 'Decimal Number'), ('IntegerField', 'Integer Number')], help_text='Select the data type for the field', max_length=50, verbose_name='Field Type')),
                ('tracker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='buddyTracker.trackerlist', verbose_name='Tracker')),
            ],
        ),
    ]
