# Generated by Django 5.0.2 on 2024-07-08 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kanban_app', '0008_timesheetsubmission'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='timesheets',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='timesheetsubmission',
            unique_together=set(),
        ),
    ]
