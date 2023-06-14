# Generated by Django 4.0.3 on 2023-06-06 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0020_alter_semester_end_date_alter_semester_start_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='student',
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=9)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('type', models.CharField(choices=[('1', 'Lecture'), ('2', 'Practical'), ('3', 'Tutorial')], max_length=200)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.venue')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='course_schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='attendance.schedule'),
        ),
    ]
