# Generated by Django 5.2.1 on 2025-05-20 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gym", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="groups",
        ),
        migrations.RemoveField(
            model_name="member",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="member",
            name="is_staff",
        ),
        migrations.RemoveField(
            model_name="member",
            name="is_superuser",
        ),
        migrations.RemoveField(
            model_name="member",
            name="last_login",
        ),
        migrations.RemoveField(
            model_name="member",
            name="password",
        ),
        migrations.RemoveField(
            model_name="member",
            name="user_permissions",
        ),
        migrations.AlterField(
            model_name="gymsession",
            name="member",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sessions",
                to="gym.member",
            ),
        ),
    ]
