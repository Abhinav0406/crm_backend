from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from .models import Client, ClientInteraction, Appointment, FollowUp, Task, Announcement, Purchase, AuditLog, serialize_field
from .serializers import ClientSerializer, ClientInteractionSerializer, AppointmentSerializer, FollowUpSerializer, TaskSerializer, AnnouncementSerializer, PurchaseSerializer, AuditLogSerializer
from apps.users.permissions import IsRoleAllowed
from rest_framework import mixins
from rest_framework import permissions
import csv
import io
import json
from datetime import datetime
from django.http import HttpResponse
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (getattr(request.user, 'role', None) in ['platform_admin', 'business_admin', 'manager'])

class ImportExportPermission(permissions.BasePermission):
    """Permission class for import/export functionality - only business admin and managers"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['business_admin', 'manager']

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales','manager','business_admin'])]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter clients by tenant for authenticated users and exclude soft-deleted clients"""
        queryset = Client.objects.all()
        # For restore and permanent_delete actions, include soft-deleted clients
        if hasattr(self, 'action') and self.action in ['restore', 'permanent_delete']:
            pass  # Don't filter out soft-deleted clients
        else:
            queryset = queryset.filter(is_deleted=False)
        user = self.request.user
        if user.is_authenticated:
            if user.is_manager:
                # Managers see customers for their tenant only
                if user.tenant:
                    queryset = queryset.filter(tenant=user.tenant)
                else:
                    queryset = Client.objects.none()
            elif user.tenant:
                queryset = queryset.filter(tenant=user.tenant)
            else:
                queryset = Client.objects.none()
        else:
            queryset = Client.objects.none()
        return queryset
    
    def create(self, request, *args, **kwargs):
        print("=== DJANGO VIEW - CREATE METHOD START ===")
        print(f"Request method: {request.method}")
        print(f"Request URL: {request.path}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request data: {request.data}")
        print(f"Request user: {request.user}")
        print(f"Request authenticated: {request.user.is_authenticated}")
        
        try:
            # Validate the data first
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("=== SERIALIZER VALIDATION FAILED ===")
                print(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            response = super().create(request, *args, **kwargs)
            print("=== DJANGO VIEW - CREATE SUCCESS ===")
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            return response
        except Exception as e:
            print("=== DJANGO VIEW - CREATE ERROR ===")
            print(f"Error in view: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"error": str(e), "detail": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test(self, request):
        """Test endpoint to check if the API is working"""
        print("=== TEST ENDPOINT CALLED ===")
        print(f"Request data: {request.data}")
        return Response({"message": "Test endpoint working", "data": request.data})
    
    def list(self, request, *args, **kwargs):
        """List clients with debugging"""
        print("=== DJANGO VIEW - LIST METHOD START ===")
        print(f"Request user: {request.user}")
        print(f"Request authenticated: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            print(f"User tenant: {request.user.tenant}")
        
        queryset = self.get_queryset()
        print(f"Queryset count: {queryset.count()}")
        print(f"Queryset SQL: {queryset.query}")
        
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        print(f"Response data count: {len(response_data)}")
        
        response = Response(response_data)
        print("=== DJANGO VIEW - LIST METHOD END ===")
        return response

    def perform_update(self, serializer):
        print(f"=== CLIENT VIEW PERFORM UPDATE ===")
        print(f"Request data: {self.request.data}")
        print(f"Request method: {self.request.method}")
        print(f"Request user: {self.request.user}")
        print(f"Request content type: {self.request.content_type}")
        print(f"Request headers: {dict(self.request.headers)}")
        
        instance = self.get_object()
        instance._auditlog_user = self.request.user
        result = serializer.save()
        print(f"=== UPDATE COMPLETED ===")
        return result

    def update(self, request, *args, **kwargs):
        print(f"=== CLIENT VIEW UPDATE METHOD ===")
        print(f"Request data: {request.data}")
        print(f"Request method: {request.method}")
        print(f"Request user: {request.user}")
        
        try:
            response = super().update(request, *args, **kwargs)
            print(f"Update successful: {response.data}")
            return response
        except Exception as e:
            print(f"Update failed with error: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def perform_destroy(self, instance):
        instance._auditlog_user = self.request.user
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance._auditlog_user = request.user
        instance.is_deleted = True
        from django.utils import timezone
        instance.deleted_at = timezone.now()
        instance.save()
        return Response({'status': 'client soft-deleted'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='trash')
    def trash(self, request):
        """List all soft-deleted clients for the tenant."""
        queryset = Client.objects.filter(is_deleted=True)
        if request.user.is_authenticated:
            user_tenant = request.user.tenant
            if user_tenant:
                queryset = queryset.filter(tenant=user_tenant)
            else:
                queryset = Client.objects.none()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        client = self.get_object()
        if client.is_deleted:
            client.is_deleted = False
            client.deleted_at = None
            client._auditlog_user = request.user
            client.save()
            # Audit log for restore
            from .models import AuditLog
            AuditLog.objects.create(
                client=client,
                action='restore',
                user=request.user,
                before=None,
                after={field.name: serialize_field(getattr(client, field.name)) for field in client._meta.fields}
            )
            return Response({'status': 'client restored'})
        return Response({'error': 'client is not deleted'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='permanent')
    def permanent_delete(self, request, pk=None):
        client = self.get_object()
        if client.is_deleted:
            client._auditlog_user = request.user
            from .models import AuditLog
            before = {field.name: serialize_field(getattr(client, field.name)) for field in client._meta.fields}
            AuditLog.objects.create(
                client=client,
                action='delete',
                user=request.user,
                before=before,
                after=None
            )
            client.delete()
            return Response({'status': 'client permanently deleted'})
        return Response({'error': 'client must be soft-deleted first'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[ImportExportPermission])
    def export_csv(self, request):
        """Export customers to CSV - only for business admin and managers"""
        try:
            queryset = self.get_queryset()
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="customers_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            # Define CSV fields
            fieldnames = [
                'first_name', 'last_name', 'email', 'phone', 'customer_type',
                'address', 'city', 'state', 'country', 'postal_code',
                'date_of_birth', 'anniversary_date', 'preferred_metal', 'preferred_stone',
                'ring_size', 'budget_range', 'lead_source', 'notes', 'community',
                'mother_tongue', 'reason_for_visit', 'age_of_end_user', 'saving_scheme',
                'catchment_area', 'next_follow_up', 'summary_notes', 'status',
                'created_at', 'updated_at', 'tags'
            ]
            
            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()
            
            for client in queryset:
                row = {}
                for field in fieldnames:
                    if field == 'date_of_birth' and client.date_of_birth:
                        row[field] = client.date_of_birth.strftime('%Y-%m-%d')
                    elif field == 'anniversary_date' and client.anniversary_date:
                        row[field] = client.anniversary_date.strftime('%Y-%m-%d')
                    elif field in ['created_at', 'updated_at']:
                        row[field] = getattr(client, field).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        value = getattr(client, field, '')
                        row[field] = str(value) if value is not None else ''
                
                # Add tags as comma-separated string
                row['tags'] = ', '.join([tag.name for tag in client.tags.all()])
                
                writer.writerow(row)
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Export failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[ImportExportPermission])
    def export_json(self, request):
        """Export customers to JSON - only for business admin and managers"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            response = HttpResponse(
                json.dumps(serializer.data, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="customers_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Export failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[ImportExportPermission])
    def import_csv(self, request):
        """Import customers from CSV - only for business admin and managers"""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            csv_file = request.FILES['file']
            
            # Validate file type
            if not csv_file.name.endswith('.csv'):
                return Response(
                    {'error': 'Please upload a CSV file'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            imported_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_data, start=2):  # Start from 2 to account for header
                    try:
                        # Clean and validate data
                        email = row.get('email', '').strip()
                        if not email:
                            errors.append(f'Row {row_num}: Email is required')
                            continue
                        
                        # Check if customer already exists
                        if Client.objects.filter(email=email, tenant=request.user.tenant, is_deleted=False).exists():
                            errors.append(f'Row {row_num}: Customer with email {email} already exists')
                            continue
                        
                        # Prepare data for creation
                        client_data = {
                            'first_name': row.get('first_name', '').strip(),
                            'last_name': row.get('last_name', '').strip(),
                            'email': email,
                            'phone': row.get('phone', '').strip(),
                            'customer_type': row.get('customer_type', 'individual'),
                            'address': row.get('address', '').strip(),
                            'city': row.get('city', '').strip(),
                            'state': row.get('state', '').strip(),
                            'country': row.get('country', '').strip(),
                            'postal_code': row.get('postal_code', '').strip(),
                            'preferred_metal': row.get('preferred_metal', '').strip(),
                            'preferred_stone': row.get('preferred_stone', '').strip(),
                            'ring_size': row.get('ring_size', '').strip(),
                            'budget_range': row.get('budget_range', '').strip(),
                            'lead_source': row.get('lead_source', '').strip(),
                            'notes': row.get('notes', '').strip(),
                            'community': row.get('community', '').strip(),
                            'mother_tongue': row.get('mother_tongue', '').strip(),
                            'reason_for_visit': row.get('reason_for_visit', '').strip(),
                            'age_of_end_user': row.get('age_of_end_user', '').strip(),
                            'saving_scheme': row.get('saving_scheme', '').strip(),
                            'catchment_area': row.get('catchment_area', '').strip(),
                            'next_follow_up': row.get('next_follow_up', '').strip(),
                            'summary_notes': row.get('summary_notes', '').strip(),
                            'status': row.get('status', 'lead'),
                            'tenant': request.user.tenant.id if request.user.tenant else None,
                        }
                        
                        # Handle date fields
                        if row.get('date_of_birth'):
                            try:
                                client_data['date_of_birth'] = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                            except ValueError:
                                pass  # Skip invalid date
                        
                        if row.get('anniversary_date'):
                            try:
                                client_data['anniversary_date'] = datetime.strptime(row['anniversary_date'], '%Y-%m-%d').date()
                            except ValueError:
                                pass  # Skip invalid date
                        
                        # Create client
                        serializer = self.get_serializer(data=client_data)
                        if serializer.is_valid():
                            client = serializer.save()
                            
                            # Handle tags if present
                            tags_str = row.get('tags', '').strip()
                            if tags_str:
                                tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                                for tag_name in tag_names:
                                    # You might want to create tags if they don't exist
                                    # For now, we'll skip tag creation
                                    pass
                            
                            imported_count += 1
                        else:
                            errors.append(f'Row {row_num}: {serializer.errors}')
                    
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
            
            return Response({
                'message': f'Import completed. {imported_count} customers imported successfully.',
                'imported_count': imported_count,
                'errors': errors
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Import failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[ImportExportPermission])
    def import_json(self, request):
        """Import customers from JSON - only for business admin and managers"""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            json_file = request.FILES['file']
            
            # Validate file type
            if not json_file.name.endswith('.json'):
                return Response(
                    {'error': 'Please upload a JSON file'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read JSON file
            json_data = json.loads(json_file.read().decode('utf-8'))
            
            if not isinstance(json_data, list):
                return Response(
                    {'error': 'JSON file should contain an array of customer objects'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            imported_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, customer_data in enumerate(json_data, start=1):
                    try:
                        # Clean and validate data
                        email = customer_data.get('email', '').strip()
                        if not email:
                            errors.append(f'Row {row_num}: Email is required')
                            continue
                        
                        # Check if customer already exists
                        if Client.objects.filter(email=email, tenant=request.user.tenant, is_deleted=False).exists():
                            errors.append(f'Row {row_num}: Customer with email {email} already exists')
                            continue
                        
                        # Prepare data for creation
                        client_data = {
                            'first_name': customer_data.get('first_name', '').strip(),
                            'last_name': customer_data.get('last_name', '').strip(),
                            'email': email,
                            'phone': customer_data.get('phone', '').strip(),
                            'customer_type': customer_data.get('customer_type', 'individual'),
                            'address': customer_data.get('address', '').strip(),
                            'city': customer_data.get('city', '').strip(),
                            'state': customer_data.get('state', '').strip(),
                            'country': customer_data.get('country', '').strip(),
                            'postal_code': customer_data.get('postal_code', '').strip(),
                            'preferred_metal': customer_data.get('preferred_metal', '').strip(),
                            'preferred_stone': customer_data.get('preferred_stone', '').strip(),
                            'ring_size': customer_data.get('ring_size', '').strip(),
                            'budget_range': customer_data.get('budget_range', '').strip(),
                            'lead_source': customer_data.get('lead_source', '').strip(),
                            'notes': customer_data.get('notes', '').strip(),
                            'community': customer_data.get('community', '').strip(),
                            'mother_tongue': customer_data.get('mother_tongue', '').strip(),
                            'reason_for_visit': customer_data.get('reason_for_visit', '').strip(),
                            'age_of_end_user': customer_data.get('age_of_end_user', '').strip(),
                            'saving_scheme': customer_data.get('saving_scheme', '').strip(),
                            'catchment_area': customer_data.get('catchment_area', '').strip(),
                            'next_follow_up': customer_data.get('next_follow_up', '').strip(),
                            'summary_notes': customer_data.get('summary_notes', '').strip(),
                            'status': customer_data.get('status', 'lead'),
                            'tenant': request.user.tenant.id if request.user.tenant else None,
                        }
                        
                        # Create client
                        serializer = self.get_serializer(data=client_data)
                        if serializer.is_valid():
                            client = serializer.save()
                            imported_count += 1
                        else:
                            errors.append(f'Row {row_num}: {serializer.errors}')
                    
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
            
            return Response({
                'message': f'Import completed. {imported_count} customers imported successfully.',
                'imported_count': imported_count,
                'errors': errors
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Import failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[ImportExportPermission])
    def download_template(self, request):
        """Download CSV template for import - only for business admin and managers"""
        try:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="customer_import_template.csv"'
            
            # Define CSV fields
            fieldnames = [
                'first_name', 'last_name', 'email', 'phone', 'customer_type',
                'address', 'city', 'state', 'country', 'postal_code',
                'date_of_birth', 'anniversary_date', 'preferred_metal', 'preferred_stone',
                'ring_size', 'budget_range', 'lead_source', 'notes', 'community',
                'mother_tongue', 'reason_for_visit', 'age_of_end_user', 'saving_scheme',
                'catchment_area', 'next_follow_up', 'summary_notes', 'status', 'tags'
            ]
            
            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()
            
            # Add example row
            example_row = {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '+1234567890',
                'customer_type': 'individual',
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
                'date_of_birth': '1990-01-01',
                'anniversary_date': '2015-06-15',
                'preferred_metal': 'Gold',
                'preferred_stone': 'Diamond',
                'ring_size': '7',
                'budget_range': '1000-5000',
                'lead_source': 'website',
                'notes': 'Interested in engagement rings',
                'community': 'General',
                'mother_tongue': 'English',
                'reason_for_visit': 'Engagement Ring',
                'age_of_end_user': '25-35',
                'saving_scheme': 'Monthly',
                'catchment_area': 'Downtown',
                'next_follow_up': 'Call next week',
                'summary_notes': 'High potential customer',
                'status': 'lead',
                'tags': 'High Value, Engagement, Gold'
            }
            writer.writerow(example_row)
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Template download failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ClientInteractionViewSet(viewsets.ModelViewSet):
    queryset = ClientInteraction.objects.all()
    serializer_class = ClientInteractionSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales'])]

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales'])]

    def get_queryset(self):
        queryset = Appointment.objects.filter(is_deleted=False)
        user = self.request.user
        if user.is_authenticated and user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
        else:
            queryset = Appointment.objects.none()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        tenant = user.tenant
        serializer.save(tenant=tenant, created_by=user, assigned_to=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(updated_by=user)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment"""
        appointment = self.get_object()
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save()
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        outcome_notes = request.data.get('outcome_notes')
        appointment.mark_completed(outcome_notes)
        return Response({'status': 'completed'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        reason = request.data.get('reason')
        appointment.cancel_appointment(reason)
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment"""
        appointment = self.get_object()
        new_date = request.data.get('new_date')
        new_time = request.data.get('new_time')
        reason = request.data.get('reason')
        
        if not new_date or not new_time:
            return Response(
                {'error': 'new_date and new_time are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_appointment = appointment.reschedule_appointment(new_date, new_time, reason)
        return Response({
            'status': 'rescheduled',
            'new_appointment_id': new_appointment.id
        })

    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send reminder for an appointment"""
        appointment = self.get_object()
        appointment.send_reminder()
        return Response({'status': 'reminder_sent'})

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get appointments for calendar view"""
        queryset = self.get_queryset()
        appointments = []
        
        for appointment in queryset:
            appointments.append({
                'id': appointment.id,
                'title': f"{appointment.client.full_name} - {appointment.purpose}",
                'start': f"{appointment.date}T{appointment.time}",
                'end': f"{appointment.date}T{appointment.time}",
                'status': appointment.status,
                'client_name': appointment.client.full_name,
                'purpose': appointment.purpose,
                'location': appointment.location,
                'assigned_to': appointment.assigned_to.get_full_name() if appointment.assigned_to else None,
            })
        
        return Response(appointments)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date__gte=today, status=Appointment.Status.SCHEDULED)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue appointments"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date__lt=today, status=Appointment.Status.SCHEDULED)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales', 'manager', 'business_admin'])]

    def get_queryset(self):
        queryset = FollowUp.objects.filter(is_deleted=False)
        user = self.request.user
        
        if user.is_authenticated and user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
            
            # For managers, filter by their store
            if user.is_manager and user.store:
                queryset = queryset.filter(
                    Q(client__assigned_to__store=user.store) |
                    Q(assigned_to__store=user.store)
                )
        else:
            queryset = FollowUp.objects.none()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by type
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__lte=end_date)
        
        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        tenant = user.tenant
        serializer.save(tenant=tenant, created_by=user, assigned_to=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(updated_by=user)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark follow-up as completed"""
        follow_up = self.get_object()
        outcome_notes = request.data.get('outcome_notes')
        follow_up.mark_completed(outcome_notes)
        return Response({'status': 'completed'})

    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send reminder for a follow-up"""
        follow_up = self.get_object()
        follow_up.send_reminder()
        return Response({'status': 'reminder_sent'})

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue follow-ups"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(due_date__lt=today, status=FollowUp.Status.PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def due_today(self, request):
        """Get follow-ups due today"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(due_date=today, status=FollowUp.Status.PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming follow-ups"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(due_date__gte=today, status=FollowUp.Status.PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales', 'manager', 'business_admin'])]

    def get_queryset(self):
        queryset = Task.objects.all()
        user = self.request.user
        if user.is_authenticated and user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
        else:
            queryset = Task.objects.none()
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        print('=== TASK CREATE DEBUG ===')
        print('User:', user)
        print('User is authenticated:', user.is_authenticated)
        print('User tenant:', getattr(user, 'tenant', None))
        tenant = user.tenant
        serializer.save(tenant=tenant, created_by=user, assigned_to=user)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales', 'manager', 'business_admin'])]

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Purchase.objects.all()
        user = self.request.user
        if user.is_authenticated and user.tenant:
            queryset = queryset.filter(client__tenant=user.tenant)
        else:
            queryset = Purchase.objects.none()
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsRoleAllowed.for_roles(['inhouse_sales','business_admin','manager'])]

    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by('-timestamp')
        client_id = self.request.query_params.get('client')
        user = self.request.user
        if user.is_authenticated and user.is_manager:
            # Managers see audit logs for customers in their tenant only
            if user.tenant:
                queryset = queryset.filter(client__tenant=user.tenant)
            else:
                queryset = AuditLog.objects.none()
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset
