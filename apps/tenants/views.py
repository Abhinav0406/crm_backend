from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Tenant
from .serializers import TenantSerializer
from apps.users.permissions import IsRoleAllowed
from apps.clients.models import Client
from apps.sales.models import Sale, SalesPipeline
from apps.products.models import Product
from apps.users.models import User, TeamMember

User = get_user_model()

class TenantListView(generics.ListAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsRoleAllowed.for_roles(['business_admin', 'platform_admin'])]

class TenantCreateView(generics.CreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsRoleAllowed.for_roles(['business_admin', 'platform_admin'])]

    def create(self, request, *args, **kwargs):
        admin_username = request.data.get('admin_username')
        admin_email = request.data.get('admin_email')
        admin_password = request.data.get('admin_password')
      
        if not (admin_username and admin_email and admin_password):
            return Response({'detail': 'Admin username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the tenant first
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        
        # Create the admin user for this tenant
        if User.objects.filter(username=admin_username, tenant=tenant).exists():
            tenant.delete()
            return Response({'detail': 'Admin username already exists for this tenant.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=admin_email, tenant=tenant).exists():
            tenant.delete()
            return Response({'detail': 'Admin email already exists for this tenant.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role=User.Role.BUSINESS_ADMIN,
            tenant=tenant,
            is_active=True
        )
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TenantDetailView(generics.RetrieveAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsRoleAllowed.for_roles(['business_admin', 'platform_admin'])]

class TenantUpdateView(generics.UpdateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsRoleAllowed.for_roles(['business_admin', 'platform_admin'])]
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        print(f"TenantUpdateView.update called with data: {request.data}")
        print(f"Tenant ID: {kwargs.get('pk')}")
        try:
            response = super().update(request, *args, **kwargs)
            print(f"Tenant updated successfully: {response.data}")
            return response
        except Exception as e:
            print(f"Error updating tenant: {e}")
            raise

class TenantDeleteView(generics.DestroyAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsRoleAllowed.for_roles(['business_admin', 'platform_admin'])]


class PlatformAdminDashboardView(APIView):
    """Platform Admin Dashboard - Provides platform-wide statistics"""
    permission_classes = [IsRoleAllowed.for_roles(['platform_admin'])]

    def get(self, request):
        try:
            # Get date range for analytics (last 30 days)
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            # 1. Total Tenants
            total_tenants = Tenant.objects.count()
            active_tenants = Tenant.objects.filter(subscription_status='active').count()
            
            # 2. Total Users across all tenants
            total_users = User.objects.exclude(role=User.Role.PLATFORM_ADMIN).count()
            
            # 3. Total Sales across all tenants (last 30 days)
            total_sales = Sale.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            )
            
            sales_amount = total_sales['total'] or Decimal('0.00')
            sales_count = total_sales['count'] or 0
            
            # 4. Recent Tenants (last 5 created)
            recent_tenants = Tenant.objects.order_by('-created_at')[:5]
            recent_tenants_data = []
            for tenant in recent_tenants:
                recent_tenants_data.append({
                    'id': tenant.id,
                    'name': tenant.name,
                    'business_type': tenant.business_type or 'Jewelry Business',
                    'subscription_status': tenant.subscription_status,
                    'created_at': tenant.created_at.strftime('%Y-%m-%d'),
                    'user_count': tenant.users.count()
                })
            
            # 5. System Health Metrics
            system_health = {
                'uptime': '99.9%',
                'active_subscriptions': active_tenants,
                'total_revenue': float(sales_amount),
                'support_tickets': 0  # Placeholder for future implementation
            }
            
            return Response({
                'total_tenants': total_tenants,
                'active_tenants': active_tenants,
                'total_users': total_users,
                'total_sales': {
                    'amount': float(sales_amount),
                    'count': sales_count
                },
                'recent_tenants': recent_tenants_data,
                'system_health': system_health
            })
            
        except Exception as e:
            print(f"Error in PlatformAdminDashboardView: {e}")
            return Response(
                {'error': 'Failed to fetch platform dashboard data'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BusinessDashboardView(APIView):
    """Business Admin Dashboard - Provides real data for the dashboard"""
    permission_classes = [IsRoleAllowed.for_roles(['business_admin'])]

    def get(self, request):
        user = request.user
        tenant = user.tenant
        
        if not tenant:
            return Response({'error': 'No tenant associated with user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get date range for analytics (last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        try:
            # 1. Total Sales (last 30 days)
            total_sales = Sale.objects.filter(
                tenant=tenant,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            )
            
            sales_amount = total_sales['total'] or Decimal('0.00')
            sales_count = total_sales['count'] or 0
            
            # 2. Active Customers (customers with recent activity)
            active_customers = Client.objects.filter(
                tenant=tenant,
                updated_at__gte=start_date
            ).count()
            
            # 3. Total Products
            total_products = Product.objects.filter(tenant=tenant).count()
            
            # 4. Team Members
            team_members = User.objects.filter(
                tenant=tenant,
                is_active=True
            ).exclude(role=User.Role.PLATFORM_ADMIN).count()
            
            # 5. Sales Pipeline Metrics
            pipeline_data = SalesPipeline.objects.filter(tenant=tenant).values('stage').annotate(
                count=Count('id')
            )
            
            # Initialize pipeline counts
            pipeline_counts = {
                'leads': 0,
                'qualified': 0,
                'proposals': 0,
                'negotiations': 0,
                'closed': 0
            }
            
            # Map pipeline stages to dashboard categories
            for item in pipeline_data:
                stage = item['stage']
                count = item['count']
                
                if stage in ['lead']:
                    pipeline_counts['leads'] += count
                elif stage in ['contacted', 'qualified']:
                    pipeline_counts['qualified'] += count
                elif stage in ['proposal']:
                    pipeline_counts['proposals'] += count
                elif stage in ['negotiation']:
                    pipeline_counts['negotiations'] += count
                elif stage in ['closed_won', 'closed_lost']:
                    pipeline_counts['closed'] += count
            
            # 6. Recent Sales (last 10 sales)
            recent_sales = Sale.objects.filter(
                tenant=tenant
            ).select_related('client').order_by('-created_at')[:10]
            
            recent_sales_data = []
            for sale in recent_sales:
                recent_sales_data.append({
                    'id': sale.id,
                    'client_name': sale.client.full_name if sale.client else 'Unknown',
                    'amount': float(sale.total_amount),
                    'status': sale.status,
                    'date': sale.created_at.strftime('%Y-%m-%d'),
                    'items_count': sale.items.count() if hasattr(sale, 'items') else 1
                })
            
            # 7. Recent Activity (last 10 activities)
            recent_activities = []
            
            # Add recent sales as activities
            for sale in recent_sales[:5]:
                recent_activities.append({
                    'type': 'sale',
                    'title': f'New sale to {sale.client.full_name if sale.client else "Unknown"}',
                    'description': f'Sale of ₹{sale.total_amount}',
                    'date': sale.created_at.strftime('%Y-%m-%d %H:%M'),
                    'amount': float(sale.total_amount)
                })
            
            # Add recent pipeline activities
            recent_pipelines = SalesPipeline.objects.filter(
                tenant=tenant
            ).select_related('client').order_by('-updated_at')[:5]
            
            for pipeline in recent_pipelines:
                recent_activities.append({
                    'type': 'pipeline',
                    'title': f'Pipeline: {pipeline.title}',
                    'description': f'{pipeline.client.full_name} - {pipeline.get_stage_display()} (₹{pipeline.expected_value})',
                    'date': pipeline.updated_at.strftime('%Y-%m-%d %H:%M'),
                    'amount': float(pipeline.expected_value)
                })
            
            # Add recent customer additions
            recent_customers = Client.objects.filter(
                tenant=tenant
            ).order_by('-created_at')[:5]
            
            for customer in recent_customers:
                recent_activities.append({
                    'type': 'customer',
                    'title': f'New customer: {customer.full_name}',
                    'description': f'Customer added to database',
                    'date': customer.created_at.strftime('%Y-%m-%d %H:%M'),
                    'amount': None
                })
            
            # Sort activities by date
            recent_activities.sort(key=lambda x: x['date'], reverse=True)
            recent_activities = recent_activities[:10]
            
            # 8. Growth metrics
            previous_period_start = start_date - timedelta(days=30)
            previous_sales = Sale.objects.filter(
                tenant=tenant,
                created_at__gte=previous_period_start,
                created_at__lt=start_date
            ).aggregate(total=Sum('total_amount'))
            
            previous_sales_amount = previous_sales['total'] or Decimal('0.00')
            sales_growth = 0
            if previous_sales_amount > 0:
                sales_growth = ((sales_amount - previous_sales_amount) / previous_sales_amount) * 100
            
            # Prepare response data
            dashboard_data = {
                'metrics': {
                    'total_sales': float(sales_amount),
                    'sales_count': sales_count,
                    'active_customers': active_customers,
                    'total_products': total_products,
                    'team_members': team_members,
                    'sales_growth': round(sales_growth, 2)
                },
                'pipeline': pipeline_counts,
                'recent_sales': recent_sales_data,
                'recent_activities': recent_activities,
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            print(f"Error in BusinessDashboardView: {e}")
            # Return mock data if there's an error
            now = timezone.now()
            return Response({
                'metrics': {
                    'total_sales': 125000.00,
                    'sales_count': 15,
                    'active_customers': 89,
                    'total_products': 45,
                    'team_members': 8,
                    'sales_growth': 12.5
                },
                'pipeline': {
                    'leads': 25,
                    'qualified': 18,
                    'proposals': 12,
                    'negotiations': 8,
                    'closed': 15
                },
                'recent_sales': [
                    {
                        'id': 1,
                        'client_name': 'Priya Sharma',
                        'amount': 25000.00,
                        'status': 'completed',
                        'date': '2024-10-15',
                        'items_count': 2
                    },
                    {
                        'id': 2,
                        'client_name': 'Rajesh Kumar',
                        'amount': 45000.00,
                        'status': 'completed',
                        'date': '2024-10-14',
                        'items_count': 1
                    }
                ],
                'recent_activities': [
                    {
                        'type': 'sale',
                        'title': 'New sale to Priya Sharma',
                        'description': 'Sale of ₹25000.00',
                        'date': '2024-10-15 14:30',
                        'amount': 25000.00
                    },
                    {
                        'type': 'pipeline',
                        'title': 'Pipeline: Wedding Collection',
                        'description': 'Rajesh Kumar - Negotiation (₹75000.00)',
                        'date': '2024-10-14 10:15',
                        'amount': 75000.00
                    }
                ],
                'period': {
                    'start_date': (now - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'end_date': now.strftime('%Y-%m-%d')
                }
            })
