# Generated by Django 5.0.6 on 2024-08-27 02:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conge', '0009_alter_leavebalance_annual_leave_balance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='holiday',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='conge.religiousholiday'),
        ),
    ]
