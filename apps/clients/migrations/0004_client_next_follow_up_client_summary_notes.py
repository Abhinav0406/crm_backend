# Generated by Django 5.2.4 on 2025-07-23 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_alter_client_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='next_follow_up',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='summary_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
