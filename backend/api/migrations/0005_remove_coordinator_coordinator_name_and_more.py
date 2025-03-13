# Generated by Django 4.2.19 on 2025-02-24 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_event_category_alter_event_end_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordinator',
            name='coordinator_name',
        ),
        migrations.AddField(
            model_name='coordinator',
            name='Faculty_coordinator_email',
            field=models.EmailField(default='', max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='Faculty_coordinator_mobile_no',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='Faculty_coordinator_name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='Student_coordinator_email',
            field=models.EmailField(default='', max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='Student_coordinator_mobile_no',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='Student_coordinator_name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
