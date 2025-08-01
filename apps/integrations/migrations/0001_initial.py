# Generated by Django 4.2.7 on 2025-07-25 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0002_tenant_google_maps_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('whatsapp', 'WhatsApp Business'), ('dukaan', 'Dukaan'), ('quicksell', 'QuickSell'), ('shopify', 'Shopify'), ('woocommerce', 'WooCommerce'), ('payment_gateway', 'Payment Gateway')], max_length=20)),
                ('name', models.CharField(help_text='Custom name for this integration', max_length=100)),
                ('api_key', models.CharField(blank=True, max_length=255, null=True)),
                ('api_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('webhook_url', models.URLField(blank=True, null=True)),
                ('config_data', models.JSONField(blank=True, default=dict)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('error', 'Error'), ('pending', 'Pending')], default='inactive', max_length=20)),
                ('is_enabled', models.BooleanField(default=False)),
                ('last_error', models.TextField(blank=True, null=True)),
                ('last_sync', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='integrations', to='tenants.tenant')),
            ],
            options={
                'verbose_name': 'Integration',
                'verbose_name_plural': 'Integrations',
                'unique_together': {('platform', 'tenant')},
            },
        ),
        migrations.CreateModel(
            name='WhatsAppIntegration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(help_text='WhatsApp Business phone number', max_length=20)),
                ('business_name', models.CharField(blank=True, max_length=100, null=True)),
                ('business_description', models.TextField(blank=True, null=True)),
                ('welcome_message', models.TextField(blank=True, null=True)),
                ('order_confirmation_template', models.CharField(blank=True, max_length=100, null=True)),
                ('order_status_template', models.CharField(blank=True, max_length=100, null=True)),
                ('auto_reply_enabled', models.BooleanField(default=False)),
                ('order_notifications_enabled', models.BooleanField(default=True)),
                ('marketing_messages_enabled', models.BooleanField(default=False)),
                ('messages_sent', models.PositiveIntegerField(default=0)),
                ('messages_received', models.PositiveIntegerField(default=0)),
                ('last_message_sent', models.DateTimeField(blank=True, null=True)),
                ('last_message_received', models.DateTimeField(blank=True, null=True)),
                ('integration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='whatsapp_config', to='integrations.integration')),
            ],
            options={
                'verbose_name': 'WhatsApp Integration',
                'verbose_name_plural': 'WhatsApp Integrations',
            },
        ),
        migrations.CreateModel(
            name='IntegrationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success')], default='info', max_length=10)),
                ('message', models.TextField()),
                ('details', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='integrations.integration')),
            ],
            options={
                'verbose_name': 'Integration Log',
                'verbose_name_plural': 'Integration Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EcommerceIntegration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_url', models.URLField(blank=True, null=True)),
                ('store_name', models.CharField(blank=True, max_length=100, null=True)),
                ('sync_products', models.BooleanField(default=True)),
                ('sync_orders', models.BooleanField(default=True)),
                ('sync_customers', models.BooleanField(default=True)),
                ('sync_inventory', models.BooleanField(default=True)),
                ('sync_interval_hours', models.PositiveIntegerField(default=24)),
                ('last_product_sync', models.DateTimeField(blank=True, null=True)),
                ('last_order_sync', models.DateTimeField(blank=True, null=True)),
                ('last_customer_sync', models.DateTimeField(blank=True, null=True)),
                ('products_synced', models.PositiveIntegerField(default=0)),
                ('orders_synced', models.PositiveIntegerField(default=0)),
                ('customers_synced', models.PositiveIntegerField(default=0)),
                ('integration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ecommerce_config', to='integrations.integration')),
            ],
            options={
                'verbose_name': 'E-commerce Integration',
                'verbose_name_plural': 'E-commerce Integrations',
            },
        ),
    ]
