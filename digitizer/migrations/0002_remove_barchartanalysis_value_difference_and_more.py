# Generated by Django 5.2.1 on 2025-05-30 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitizer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='barchartanalysis',
            name='value_difference',
        ),
        migrations.AddField(
            model_name='barchartanalysis',
            name='y1_value',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='barchartanalysis',
            name='y2_value',
            field=models.IntegerField(null=True),
        ),
    ]
