# Generated by Django 5.2.4 on 2025-07-20 18:20

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(help_text='Unique employee identifier', max_length=20, unique=True)),
                ('department', models.CharField(blank=True, help_text='Department or team', max_length=50, null=True)),
                ('position', models.CharField(blank=True, help_text='Job position or title', max_length=100, null=True)),
                ('hire_date', models.DateField(default=django.utils.timezone.now, help_text='Date when team member was hired')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended'), ('on_leave', 'On Leave')], default='active', help_text='Current status of the team member', max_length=20)),
                ('performance_rating', models.CharField(blank=True, choices=[('excellent', 'Excellent'), ('good', 'Good'), ('average', 'Average'), ('below_average', 'Below Average'), ('poor', 'Poor')], help_text='Current performance rating', max_length=20, null=True)),
                ('sales_target', models.DecimalField(decimal_places=2, default=0.0, help_text='Monthly sales target', max_digits=10)),
                ('current_sales', models.DecimalField(decimal_places=2, default=0.0, help_text='Current month sales', max_digits=10)),
                ('skills', models.JSONField(blank=True, default=list, help_text='List of skills and competencies')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the team member', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('manager', models.ForeignKey(blank=True, help_text='Direct manager or supervisor', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to='users.teammember')),
                ('user', models.OneToOneField(help_text='Associated user account', on_delete=django.db.models.deletion.CASCADE, related_name='team_member', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Team Member',
                'verbose_name_plural': 'Team Members',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TeamMemberActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('sale', 'Sale Made'), ('lead_created', 'Lead Created'), ('customer_contact', 'Customer Contact'), ('task_completed', 'Task Completed'), ('performance_review', 'Performance Review')], help_text='Type of activity performed', max_length=20)),
                ('description', models.TextField(help_text='Description of the activity')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional data related to the activity')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('team_member', models.ForeignKey(help_text='Team member who performed the activity', on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='users.teammember')),
            ],
            options={
                'verbose_name': 'Team Member Activity',
                'verbose_name_plural': 'Team Member Activities',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TeamMemberPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(help_text='Month for this performance record')),
                ('sales_target', models.DecimalField(decimal_places=2, help_text='Monthly sales target', max_digits=10)),
                ('actual_sales', models.DecimalField(decimal_places=2, default=0.0, help_text='Actual sales achieved', max_digits=10)),
                ('leads_generated', models.PositiveIntegerField(default=0, help_text='Number of leads generated')),
                ('deals_closed', models.PositiveIntegerField(default=0, help_text='Number of deals closed')),
                ('customer_satisfaction', models.DecimalField(blank=True, decimal_places=2, help_text='Customer satisfaction rating (1-5)', max_digits=3, null=True)),
                ('notes', models.TextField(blank=True, help_text='Performance notes and comments', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team_member', models.ForeignKey(help_text='Team member performance record', on_delete=django.db.models.deletion.CASCADE, related_name='performance_records', to='users.teammember')),
            ],
            options={
                'verbose_name': 'Team Member Performance',
                'verbose_name_plural': 'Team Member Performance',
                'ordering': ['-month'],
                'unique_together': {('team_member', 'month')},
            },
        ),
    ]
