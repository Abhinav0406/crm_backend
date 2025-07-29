from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard-stats/', views.SimpleDashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Sales Pipeline Analytics
    path('pipeline/', views.SalesPipelineAnalyticsView.as_view(), name='pipeline-analytics'),
    
    # Revenue Analytics
    path('revenue/', views.RevenueAnalyticsView.as_view(), name='revenue-analytics'),
    
    # Metrics
    path('metrics/', views.MetricsListView.as_view(), name='metrics-list'),
    path('metrics/<str:metric_type>/', views.MetricDetailView.as_view(), name='metric-detail'),
    
    # Reports
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/generate/', views.ReportGenerateView.as_view(), name='report-generate'),
    path('reports/<int:pk>/download/', views.ReportDownloadView.as_view(), name='report-download'),
    
    # Events
    path('events/', views.AnalyticsEventListView.as_view(), name='event-list'),
    path('events/track/', views.AnalyticsEventTrackView.as_view(), name='event-track'),
    
    # Widgets
    path('widgets/', views.DashboardWidgetListView.as_view(), name='widget-list'),
    path('widgets/create/', views.DashboardWidgetCreateView.as_view(), name='widget-create'),
    path('widgets/<int:pk>/', views.DashboardWidgetDetailView.as_view(), name='widget-detail'),
    path('widgets/<int:pk>/update/', views.DashboardWidgetUpdateView.as_view(), name='widget-update'),
    path('widgets/<int:pk>/delete/', views.DashboardWidgetDeleteView.as_view(), name='widget-delete'),
] 