# Generated by Django 4.0.3 on 2023-06-01 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0015_remove_userprofile_dob_remove_userprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='yos',
            field=models.CharField(choices=[('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year')], max_length=250, null=True),
        ),
    ]
