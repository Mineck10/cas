# Generated by Django 4.0.3 on 2023-06-07 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0022_rename_type_schedule_session_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='venue',
            old_name='venue_id',
            new_name='block',
        ),
        migrations.RenameField(
            model_name='venue',
            old_name='name',
            new_name='number',
        ),
    ]