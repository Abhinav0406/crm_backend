from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q, F, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import AnalyticsEvent, BusinessMetrics, DashboardWidget, Report
from .serializers import AnalyticsEventSerializer, BusinessMetricsSerializer, DashboardWidgetSerializer, ReportSerializer
from apps.sales.models import Sale, SalesPipeline
from apps.clients.models import Client
from apps.products.models import Product

class DashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive dashboard analytics"""
        try:
            tenant = request.user.tenant
            
            # Date ranges
            today = timezone.now().date()
            this_month = today.replace(day=1)
            last_month = (this_month - timedelta(days=1)).replace(day=1)
            
            # Sales Analytics
            sales_data = self._get_sales_analytics(tenant, today, this_month, last_month)
            
            # Pipeline Analytics
            pipeline_data = self._get_pipeline_analytics(tenant)
            
            # Conversion Analytics
            conversion_data = self._get_conversion_analytics(tenant, this_month)
            
            # Revenue Analytics
            revenue_data = self._get_revenue_analytics(tenant, this_month, last_month)
            
            return Response({
                'sales': sales_data,
                'pipeline': pipeline_data,
                'conversion': conversion_data,
                'revenue': revenue_data,
            })
        except Exception as e:
            print(f"Error in DashboardView: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimpleDashboardStatsView(generics.GenericAPIView):
    """Simple dashboard stats for In-house Sales dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get simple dashboard stats"""
        try:
            tenant = request.user.tenant
            
            # Total sales (revenue)
            total_sales = Sale.objects.filter(
                tenant=tenant,
                status__in=['confirmed', 'processing', 'shipped', 'delivered']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            # Active customers (all customers for now)
            active_customers = Client.objects.filter(
                tenant=tenant
            ).count()
            
            # Total orders
            total_orders = Sale.objects.filter(
                tenant=tenant
            ).count()
            
            # Total announcements
            from apps.announcements.models import Announcement
            total_announcements = Announcement.objects.filter(
                tenant=tenant,
                is_active=True
            ).count()
            
            # Recent sales (last 5)
            recent_sales = Sale.objects.filter(
                tenant=tenant
            ).order_by('-created_at')[:5].values(
                'id', 'total_amount', 'status', 'created_at'
            )
            
            # Sales trend (last 7 days)
            seven_days_ago = timezone.now().date() - timedelta(days=7)
            sales_trend = Sale.objects.filter(
                tenant=tenant,
                created_at__date__gte=seven_days_ago
            ).values('created_at__date').annotate(
                daily_sales=Sum('total_amount')
            ).order_by('created_at__date')
            
            return Response({
                'total_sales': float(total_sales),
                'active_customers': active_customers,
                'total_orders': total_orders,
                'total_announcements': total_announcements,
                'recent_sales': list(recent_sales),
                'sales_trend': list(sales_trend)
            })
            
        except Exception as e:
            print(f"Error in SimpleDashboardStatsView: {str(e)}")
            return Response(
                {
                    'total_sales': 0,
                    'active_customers': 0,
                    'total_orders': 0,
                    'total_announcements': 0,
                    'recent_sales': [],
                    'sales_trend': []
                },
                status=status.HTTP_200_OK
            )
    
    def _get_sales_analytics(self, tenant, today, this_month, last_month):
        """Get sales analytics data"""
        # Total sales
        total_sales = Sale.objects.filter(tenant=tenant).count()
        monthly_sales = Sale.objects.filter(
            tenant=tenant,
            created_at__gte=this_month
        ).count()
        
        # Revenue
        total_revenue = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        monthly_revenue = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Average order value
        avg_order_value = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0')
        
        return {
            'total_sales': total_sales,
            'monthly_sales': monthly_sales,
            'total_revenue': float(total_revenue),
            'monthly_revenue': float(monthly_revenue),
            'avg_order_value': float(avg_order_value),
        }
    
    def _get_pipeline_analytics(self, tenant):
        """Get pipeline analytics data"""
        # Pipeline stages
        stages = SalesPipeline.Stage.choices
        stage_data = {}
        
        for stage_code, stage_name in stages:
            count = SalesPipeline.objects.filter(
                tenant=tenant,
                stage=stage_code
            ).count()
            
            value = SalesPipeline.objects.filter(
                tenant=tenant,
                stage=stage_code
            ).aggregate(total=Sum('expected_value'))['total'] or Decimal('0')
            
            stage_data[stage_code] = {
                'name': stage_name,
                'count': count,
                'value': float(value),
            }
        
        # Total pipeline value (excluding closed lost)
        total_pipeline_value = SalesPipeline.objects.filter(
            tenant=tenant
        ).exclude(
            stage=SalesPipeline.Stage.CLOSED_LOST
        ).aggregate(total=Sum('expected_value'))['total'] or Decimal('0')
        
        # Active deals (excluding closed lost)
        active_deals = SalesPipeline.objects.filter(
            tenant=tenant
        ).exclude(
            stage=SalesPipeline.Stage.CLOSED_LOST
        ).count()
        
        return {
            'stages': stage_data,
            'total_pipeline_value': float(total_pipeline_value),
            'active_deals': active_deals,
        }
    
    def _get_conversion_analytics(self, tenant, this_month):
        """Get conversion analytics data"""
        # Lead to customer conversion
        total_leads = SalesPipeline.objects.filter(
            tenant=tenant,
            stage='lead'
        ).count()
        
        converted_leads = SalesPipeline.objects.filter(
            tenant=tenant,
            stage='closed_won'
        ).count()
        
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Monthly conversion
        monthly_leads = SalesPipeline.objects.filter(
            tenant=tenant,
            stage='lead',
            created_at__gte=this_month
        ).count()
        
        monthly_converted = SalesPipeline.objects.filter(
            tenant=tenant,
            stage='closed_won',
            actual_close_date__gte=this_month
        ).count()
        
        monthly_conversion_rate = (monthly_converted / monthly_leads * 100) if monthly_leads > 0 else 0
        
        return {
            'total_leads': total_leads,
            'converted_leads': converted_leads,
            'conversion_rate': round(conversion_rate, 2),
            'monthly_leads': monthly_leads,
            'monthly_converted': monthly_converted,
            'monthly_conversion_rate': round(monthly_conversion_rate, 2),
        }
    
    def _get_revenue_analytics(self, tenant, this_month, last_month):
        """Get revenue analytics data"""
        # Current month revenue
        current_revenue = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Last month revenue
        last_month_revenue = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__gte=last_month,
            created_at__lt=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Revenue growth
        revenue_growth = 0
        if last_month_revenue > 0:
            revenue_growth = ((current_revenue - last_month_revenue) / last_month_revenue) * 100
        
        # Revenue by product category (if available)
        revenue_by_product = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__gte=this_month
        ).values('items__product__category').annotate(
            total=Sum('items__total_price')
        ).order_by('-total')[:5]
        
        return {
            'current_revenue': float(current_revenue),
            'last_month_revenue': float(last_month_revenue),
            'revenue_growth': round(revenue_growth, 2),
            'revenue_by_product': list(revenue_by_product),
        }

class SalesPipelineAnalyticsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get detailed sales pipeline analytics"""
        tenant = request.user.tenant
        
        # Pipeline stage distribution
        stage_distribution = SalesPipeline.objects.filter(
            tenant=tenant
        ).values('stage').annotate(
            count=Count('id'),
            total_value=Sum('expected_value')
        ).order_by('stage')
        
        # Pipeline velocity (time in each stage)
        pipeline_velocity = self._calculate_pipeline_velocity(tenant)
        
        # Win/loss analysis
        win_loss_analysis = self._get_win_loss_analysis(tenant)
        
        # Deal size analysis
        deal_size_analysis = self._get_deal_size_analysis(tenant)
        
        return Response({
            'stage_distribution': list(stage_distribution),
            'pipeline_velocity': pipeline_velocity,
            'win_loss_analysis': win_loss_analysis,
            'deal_size_analysis': deal_size_analysis,
        })
    
    def _calculate_pipeline_velocity(self, tenant):
        """Calculate average time spent in each pipeline stage"""
        velocity_data = {}
        
        for stage_code, stage_name in SalesPipeline.Stage.choices:
            pipelines = SalesPipeline.objects.filter(
                tenant=tenant,
                stage=stage_code
            )
            
            if pipelines.exists():
                # Calculate average time in stage (simplified)
                avg_days = pipelines.aggregate(
                    avg_days=Avg(F('updated_at') - F('created_at'))
                )['avg_days']
                
                velocity_data[stage_code] = {
                    'stage_name': stage_name,
                    'avg_days': avg_days.days if avg_days else 0,
                    'count': pipelines.count(),
                }
        
        return velocity_data
    
    def _get_win_loss_analysis(self, tenant):
        """Get win/loss analysis"""
        total_deals = SalesPipeline.objects.filter(
            tenant=tenant,
            is_closed=True
        ).count()
        
        won_deals = SalesPipeline.objects.filter(
            tenant=tenant,
            stage='closed_won'
        ).count()
        
        lost_deals = SalesPipeline.objects.filter(
            tenant=tenant,
            stage='closed_lost'
        ).count()
        
        win_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
        loss_rate = (lost_deals / total_deals * 100) if total_deals > 0 else 0
        
        return {
            'total_deals': total_deals,
            'won_deals': won_deals,
            'lost_deals': lost_deals,
            'win_rate': round(win_rate, 2),
            'loss_rate': round(loss_rate, 2),
        }
    
    def _get_deal_size_analysis(self, tenant):
        """Get deal size analysis"""
        deals = SalesPipeline.objects.filter(
            tenant=tenant,
            expected_value__gt=0
        )
        
        if deals.exists():
            avg_deal_size = deals.aggregate(avg=Avg('expected_value'))['avg']
            max_deal_size = deals.aggregate(max=Max('expected_value'))['max']
            min_deal_size = deals.aggregate(min=Min('expected_value'))['min']
        else:
            avg_deal_size = max_deal_size = min_deal_size = 0
        
        return {
            'avg_deal_size': float(avg_deal_size),
            'max_deal_size': float(max_deal_size),
            'min_deal_size': float(min_deal_size),
        }

class RevenueAnalyticsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get detailed revenue analytics"""
        tenant = request.user.tenant
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        # Revenue trends
        revenue_trends = self._get_revenue_trends(tenant, start_date, end_date)
        
        # Revenue by sales rep
        revenue_by_rep = self._get_revenue_by_rep(tenant, start_date, end_date)
        
        # Revenue by product
        revenue_by_product = self._get_revenue_by_product(tenant, start_date, end_date)
        
        # Revenue by store/location
        revenue_by_store = self._get_revenue_by_store(tenant, start_date, end_date)
        
        return Response({
            'revenue_trends': revenue_trends,
            'revenue_by_rep': revenue_by_rep,
            'revenue_by_product': revenue_by_product,
            'revenue_by_store': revenue_by_store,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            }
        })
    
    def _get_revenue_trends(self, tenant, start_date, end_date):
        """Get revenue trends over time"""
        sales = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__date__range=[start_date, end_date]
        ).values('created_at__date').annotate(
            daily_revenue=Sum('total_amount')
        ).order_by('created_at__date')
        
        return list(sales)
    
    def _get_revenue_by_rep(self, tenant, start_date, end_date):
        """Get revenue by sales representative"""
        return Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__date__range=[start_date, end_date]
        ).values('sales_representative__first_name', 'sales_representative__last_name').annotate(
            total_revenue=Sum('total_amount'),
            sale_count=Count('id')
        ).order_by('-total_revenue')
    
    def _get_revenue_by_product(self, tenant, start_date, end_date):
        """Get revenue by product"""
        return Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__date__range=[start_date, end_date]
        ).values('items__product__name').annotate(
            total_revenue=Sum('items__total_price'),
            units_sold=Sum('items__quantity')
        ).order_by('-total_revenue')
    
    def _get_revenue_by_store(self, tenant, start_date, end_date):
        """Get revenue by store/location"""
        return Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered'],
            created_at__date__range=[start_date, end_date]
        ).values('sales_representative__store__name').annotate(
            total_revenue=Sum('total_amount'),
            sale_count=Count('id')
        ).order_by('-total_revenue')

class MetricsListView(generics.ListAPIView):
    queryset = BusinessMetrics.objects.all()
    serializer_class = BusinessMetricsSerializer

class MetricDetailView(generics.RetrieveAPIView):
    queryset = BusinessMetrics.objects.all()
    serializer_class = BusinessMetricsSerializer

class ReportListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class ReportDetailView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class ReportGenerateView(generics.GenericAPIView):
    def post(self, request, pk):
        return Response({"message": "Report generation endpoint"})

class ReportDownloadView(generics.GenericAPIView):
    def get(self, request, pk):
        return Response({"message": "Report download endpoint"})

class AnalyticsEventListView(generics.ListAPIView):
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer

class AnalyticsEventTrackView(generics.GenericAPIView):
    def post(self, request):
        return Response({"message": "Event tracking endpoint"})

class DashboardWidgetListView(generics.ListAPIView):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer

class DashboardWidgetCreateView(generics.CreateAPIView):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer

class DashboardWidgetDetailView(generics.RetrieveAPIView):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer

class DashboardWidgetUpdateView(generics.UpdateAPIView):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer

class DashboardWidgetDeleteView(generics.DestroyAPIView):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
