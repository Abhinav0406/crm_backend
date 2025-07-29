from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # Integrations
    path('list/', views.IntegrationListView.as_view(), name='integration-list'),
    path('create/', views.IntegrationCreateView.as_view(), name='integration-create'),
    path('<int:pk>/', views.IntegrationDetailView.as_view(), name='integration-detail'),
    path('<int:pk>/update/', views.IntegrationUpdateView.as_view(), name='integration-update'),
    path('<int:pk>/delete/', views.IntegrationDeleteView.as_view(), name='integration-delete'),
    path('<int:pk>/test/', views.IntegrationTestView.as_view(), name='integration-test'),
    
    # WhatsApp Integration
    path('whatsapp/', views.WhatsAppIntegrationView.as_view(), name='whatsapp-config'),
    path('whatsapp/send-message/', views.WhatsAppSendMessageView.as_view(), name='whatsapp-send'),
    
    # E-commerce Integration
    path('ecommerce/', views.EcommerceIntegrationView.as_view(), name='ecommerce-config'),
    path('ecommerce/sync/', views.EcommerceSyncView.as_view(), name='ecommerce-sync'),
    
    # Logs
    path('logs/', views.IntegrationLogListView.as_view(), name='log-list'),
] 