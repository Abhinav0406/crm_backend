from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Sale, SaleItem, SalesPipeline
from .serializers import SaleSerializer, SaleItemSerializer, SalesPipelineSerializer


class SaleListView(generics.ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter sales by tenant and add search/filtering"""
        queryset = Sale.objects.filter(tenant=self.request.user.tenant)
        
        # Search by order number or client name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__range=[start_date, end_date]
            )
        
        return queryset.order_by('-created_at')


class SaleCreateView(generics.CreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set tenant and generate order number"""
        serializer.save(
            tenant=self.request.user.tenant,
            sales_representative=self.request.user
        )


class SaleDetailView(generics.RetrieveAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Sale.objects.filter(tenant=self.request.user.tenant)


class SaleUpdateView(generics.UpdateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Sale.objects.filter(tenant=self.request.user.tenant)


class SaleDeleteView(generics.DestroyAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Sale.objects.filter(tenant=self.request.user.tenant)


class SalesPipelineListView(generics.ListAPIView):
    queryset = SalesPipeline.objects.all()
    serializer_class = SalesPipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter pipelines by tenant and add search/filtering"""
        queryset = SalesPipeline.objects.filter(tenant=self.request.user.tenant)
        
        # Search by title or client name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search)
            )
        
        # Filter by stage
        stage_filter = self.request.query_params.get('stage', None)
        if stage_filter:
            queryset = queryset.filter(stage=stage_filter)
        
        # Filter by sales rep
        rep_filter = self.request.query_params.get('sales_rep', None)
        if rep_filter:
            queryset = queryset.filter(sales_representative_id=rep_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__range=[start_date, end_date]
            )
        
        return queryset.order_by('-updated_at')


class SalesPipelineCreateView(generics.CreateAPIView):
    queryset = SalesPipeline.objects.all()
    serializer_class = SalesPipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set tenant and sales representative"""
        try:
            serializer.save(
                tenant=self.request.user.tenant,
                sales_representative=self.request.user
            )
        except Exception as e:
            print(f"Error creating pipeline: {str(e)}")
            raise


class SalesPipelineDetailView(generics.RetrieveAPIView):
    queryset = SalesPipeline.objects.all()
    serializer_class = SalesPipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SalesPipeline.objects.filter(tenant=self.request.user.tenant)


class SalesPipelineUpdateView(generics.UpdateAPIView):
    queryset = SalesPipeline.objects.all()
    serializer_class = SalesPipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SalesPipeline.objects.filter(tenant=self.request.user.tenant)


class SalesPipelineDeleteView(generics.DestroyAPIView):
    queryset = SalesPipeline.objects.all()
    serializer_class = SalesPipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SalesPipeline.objects.filter(tenant=self.request.user.tenant)


class PipelineStageTransitionView(generics.GenericAPIView):
    """Move pipeline to next stage"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            pipeline = SalesPipeline.objects.get(
                pk=pk,
                tenant=request.user.tenant
            )
            
            new_stage = request.data.get('stage')
            if new_stage not in dict(SalesPipeline.Stage.choices):
                return Response(
                    {'error': 'Invalid stage'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Move to new stage
            pipeline.move_to_stage(new_stage)
            
            return Response({
                'message': f'Pipeline moved to {pipeline.get_stage_display()}',
                'pipeline': SalesPipelineSerializer(pipeline).data
            })
            
        except SalesPipeline.DoesNotExist:
            return Response(
                {'error': 'Pipeline not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PipelineDashboardView(generics.GenericAPIView):
    """Get pipeline dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            tenant = request.user.tenant
            
            # Pipeline summary by stage
            stage_summary = {}
            for stage_code, stage_name in SalesPipeline.Stage.choices:
                pipelines = SalesPipeline.objects.filter(
                    tenant=tenant,
                    stage=stage_code
                )
                
                count = pipelines.count()
                value = pipelines.aggregate(
                    total=Sum('expected_value')
                )['total'] or Decimal('0')
                
                stage_summary[stage_code] = {
                    'name': stage_name,
                    'count': count,
                    'value': float(value),
                    'percentage': 0  # Will be calculated below
                }
            
            # Calculate percentages
            total_pipelines = sum(stage['count'] for stage in stage_summary.values())
            if total_pipelines > 0:
                for stage in stage_summary.values():
                    stage['percentage'] = round((stage['count'] / total_pipelines) * 100, 1)
            
            # Recent activities
            recent_pipelines = SalesPipeline.objects.filter(
                tenant=tenant
            ).order_by('-updated_at')[:10]
            
            # Upcoming actions - filter out closed pipelines
            upcoming_actions = SalesPipeline.objects.filter(
                tenant=tenant,
                next_action_date__gte=timezone.now()
            ).exclude(
                stage__in=[SalesPipeline.Stage.CLOSED_WON, SalesPipeline.Stage.CLOSED_LOST]
            ).order_by('next_action_date')[:5]
            
            return Response({
                'stage_summary': stage_summary,
                'recent_pipelines': SalesPipelineSerializer(recent_pipelines, many=True).data,
                'upcoming_actions': SalesPipelineSerializer(upcoming_actions, many=True).data,
            })
        except Exception as e:
            print(f"Error in PipelineDashboardView: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SalesExportView(generics.GenericAPIView):
    """Export sales data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export sales data in various formats"""
        format_type = request.query_params.get('format', 'json')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Sale.objects.filter(tenant=request.user.tenant)
        
        # Apply date filters if provided
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__range=[start_date, end_date]
            )
        
        if format_type == 'json':
            serializer = SaleSerializer(queryset, many=True)
            return Response(serializer.data)
        elif format_type == 'csv':
            # TODO: Implement CSV export
            return Response({'message': 'CSV export not implemented yet'})
        else:
            return Response(
                {'error': 'Unsupported format'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PipelineExportView(generics.GenericAPIView):
    """Export pipeline data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export pipeline data in various formats"""
        format_type = request.query_params.get('format', 'json')
        stage_filter = request.query_params.get('stage')
        
        queryset = SalesPipeline.objects.filter(tenant=request.user.tenant)
        
        # Apply stage filter if provided
        if stage_filter:
            queryset = queryset.filter(stage=stage_filter)
        
        if format_type == 'json':
            serializer = SalesPipelineSerializer(queryset, many=True)
            return Response(serializer.data)
        elif format_type == 'csv':
            # TODO: Implement CSV export
            return Response({'message': 'CSV export not implemented yet'})
        else:
            return Response(
                {'error': 'Unsupported format'},
                status=status.HTTP_400_BAD_REQUEST
            )
