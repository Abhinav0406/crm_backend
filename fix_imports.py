#!/usr/bin/env python
"""
Script to add basic content to all missing files to fix import errors.
"""

import os

# Files to create with basic content
files_content = {
    'apps/products/views.py': '''from rest_framework import generics
from .models import Product, Category, ProductVariant
from .serializers import ProductSerializer, CategorySerializer, ProductVariantSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductVariantListView(generics.ListAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

class ProductVariantCreateView(generics.CreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

class ProductVariantDetailView(generics.RetrieveAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

class ProductVariantUpdateView(generics.UpdateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

class ProductVariantDeleteView(generics.DestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
''',
    
    'apps/products/serializers.py': '''from rest_framework import serializers
from .models import Product, Category, ProductVariant

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'
''',
    
    'apps/integrations/views.py': '''from rest_framework import generics
from .models import Integration, WhatsAppIntegration, EcommerceIntegration, IntegrationLog
from .serializers import IntegrationSerializer, WhatsAppIntegrationSerializer, EcommerceIntegrationSerializer, IntegrationLogSerializer

class IntegrationListView(generics.ListAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationCreateView(generics.CreateAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationDetailView(generics.RetrieveAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationUpdateView(generics.UpdateAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationDeleteView(generics.DestroyAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationTestView(generics.GenericAPIView):
    def post(self, request, pk):
        return Response({"message": "Integration test endpoint"})

class WhatsAppIntegrationView(generics.GenericAPIView):
    def get(self, request):
        return Response({"message": "WhatsApp integration config"})

class WhatsAppSendMessageView(generics.GenericAPIView):
    def post(self, request):
        return Response({"message": "WhatsApp send message endpoint"})

class EcommerceIntegrationView(generics.GenericAPIView):
    def get(self, request):
        return Response({"message": "E-commerce integration config"})

class EcommerceSyncView(generics.GenericAPIView):
    def post(self, request):
        return Response({"message": "E-commerce sync endpoint"})

class IntegrationLogListView(generics.ListAPIView):
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
''',
    
    'apps/integrations/serializers.py': '''from rest_framework import serializers
from .models import Integration, WhatsAppIntegration, EcommerceIntegration, IntegrationLog

class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = '__all__'

class WhatsAppIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppIntegration
        fields = '__all__'

class EcommerceIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcommerceIntegration
        fields = '__all__'

class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = '__all__'
''',
    
    'apps/analytics/views.py': '''from rest_framework import generics
from rest_framework.response import Response
from .models import AnalyticsEvent, BusinessMetrics, DashboardWidget, Report
from .serializers import AnalyticsEventSerializer, BusinessMetricsSerializer, DashboardWidgetSerializer, ReportSerializer

class DashboardView(generics.GenericAPIView):
    def get(self, request):
        return Response({"message": "Dashboard endpoint"})

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
''',
    
    'apps/analytics/serializers.py': '''from rest_framework import serializers
from .models import AnalyticsEvent, BusinessMetrics, DashboardWidget, Report

class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = '__all__'

class BusinessMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMetrics
        fields = '__all__'

class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
''',
    
    'apps/automation/views.py': '''from rest_framework import generics
from rest_framework.response import Response
from .models import AutomationWorkflow, AutomationExecution, ScheduledTask, TaskExecution
from .serializers import AutomationWorkflowSerializer, AutomationExecutionSerializer, ScheduledTaskSerializer, TaskExecutionSerializer

class AutomationWorkflowListView(generics.ListAPIView):
    queryset = AutomationWorkflow.objects.all()
    serializer_class = AutomationWorkflowSerializer

class AutomationWorkflowCreateView(generics.CreateAPIView):
    queryset = AutomationWorkflow.objects.all()
    serializer_class = AutomationWorkflowSerializer

class AutomationWorkflowDetailView(generics.RetrieveAPIView):
    queryset = AutomationWorkflow.objects.all()
    serializer_class = AutomationWorkflowSerializer

class AutomationWorkflowUpdateView(generics.UpdateAPIView):
    queryset = AutomationWorkflow.objects.all()
    serializer_class = AutomationWorkflowSerializer

class AutomationWorkflowDeleteView(generics.DestroyAPIView):
    queryset = AutomationWorkflow.objects.all()
    serializer_class = AutomationWorkflowSerializer

class AutomationWorkflowExecuteView(generics.GenericAPIView):
    def post(self, request, pk):
        return Response({"message": "Workflow execution endpoint"})

class AutomationExecutionListView(generics.ListAPIView):
    queryset = AutomationExecution.objects.all()
    serializer_class = AutomationExecutionSerializer

class AutomationExecutionDetailView(generics.RetrieveAPIView):
    queryset = AutomationExecution.objects.all()
    serializer_class = AutomationExecutionSerializer

class ScheduledTaskListView(generics.ListAPIView):
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer

class ScheduledTaskCreateView(generics.CreateAPIView):
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer

class ScheduledTaskDetailView(generics.RetrieveAPIView):
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer

class ScheduledTaskUpdateView(generics.UpdateAPIView):
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer

class ScheduledTaskDeleteView(generics.DestroyAPIView):
    queryset = ScheduledTask.objects.all()
    serializer_class = ScheduledTaskSerializer

class ScheduledTaskExecuteView(generics.GenericAPIView):
    def post(self, request, pk):
        return Response({"message": "Task execution endpoint"})

class TaskExecutionListView(generics.ListAPIView):
    queryset = TaskExecution.objects.all()
    serializer_class = TaskExecutionSerializer

class TaskExecutionDetailView(generics.RetrieveAPIView):
    queryset = TaskExecution.objects.all()
    serializer_class = TaskExecutionSerializer
''',
    
    'apps/automation/serializers.py': '''from rest_framework import serializers
from .models import AutomationWorkflow, AutomationExecution, ScheduledTask, TaskExecution

class AutomationWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationWorkflow
        fields = '__all__'

class AutomationExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationExecution
        fields = '__all__'

class ScheduledTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTask
        fields = '__all__'

class TaskExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecution
        fields = '__all__'
'''
}

def main():
    print("Adding basic content to missing files...")
    
    for file_path, content in files_content.items():
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Created: {file_path}")
        except Exception as e:
            print(f"Error creating {file_path}: {e}")
    
    print("Done!")

if __name__ == '__main__':
    main() 