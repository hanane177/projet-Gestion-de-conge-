# Generated by Django 5.0.6 on 2024-08-24 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_userprofile_cin_userprofile_division_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='annual_leave_days',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='exceptional_leave_days',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ppr',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
