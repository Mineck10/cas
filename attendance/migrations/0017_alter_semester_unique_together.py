# Generated by Django 4.0.3 on 2023-06-02 04:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0016_student_yos'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='semester',
            unique_together=set(),
        ),
    ]