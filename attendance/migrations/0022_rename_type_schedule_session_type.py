# Generated by Django 4.0.3 on 2023-06-07 02:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0021_remove_course_student_schedule_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='type',
            new_name='session_type',
        ),
    ]
