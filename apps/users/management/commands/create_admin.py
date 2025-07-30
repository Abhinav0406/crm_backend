from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.tenants.models import Tenant

class Command(BaseCommand):
    help = 'Create a superuser for admin access'

    def handle(self, *args, **options):
        # Create default tenant if it doesn't exist
        default_tenant, created = Tenant.objects.get_or_create(
            slug='platform',
            defaults={
                'name': 'Platform Admin',
                'business_type': 'platform',
                'subscription_plan': 'enterprise',
                'max_users': 1000,
                'max_storage_gb': 1000,
            }
        )
        
        if created:
            self.stdout.write(f"Created default tenant: {default_tenant.name}")
        
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write("Admin user already exists!")
            user = User.objects.get(username='admin')
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Email: {user.email}")
            return
        
        # Create admin user
        try:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@jewelrycrm.com',
                password='admin123456',
                first_name='Platform',
                last_name='Admin',
                role='platform_admin',
                is_superuser=True,
                is_staff=True,
                is_active=True,
                tenant=default_tenant
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Admin user created successfully!')
            )
            self.stdout.write(f"Username: {admin_user.username}")
            self.stdout.write(f"Password: admin123456")
            self.stdout.write(f"Email: {admin_user.email}")
            self.stdout.write(f"Role: {admin_user.role}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {e}')
            ) 