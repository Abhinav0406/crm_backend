from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, TeamMember, TeamMemberActivity, TeamMemberPerformance
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    TeamMemberSerializer, TeamMemberListSerializer, TeamMemberCreateSerializer,
    TeamMemberUpdateSerializer, TeamMemberActivitySerializer, TeamMemberPerformanceSerializer, TeamStatsSerializer,
    MessagingUserSerializer
)
from apps.users.permissions import IsRoleAllowed


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update current user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({
                'error': 'Both old_password and new_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({
                'error': 'Old password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({
                'error': e.messages
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return User.objects.all()
        if user.is_business_admin or user.is_manager:
            return User.objects.filter(tenant=user.tenant)
        # Otherwise, only themselves
        return User.objects.filter(id=user.id)


class UserCreateView(generics.CreateAPIView):
    """
    Create a new user (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsRoleAllowed.for_roles(['platform_admin', 'business_admin', 'manager'])]

    def create(self, request, *args, **kwargs):
        user = request.user

        # Only allow platform admin, business admin, or manager to create users
        allowed_roles = ['platform_admin', 'business_admin', 'manager']
        if user.role not in allowed_roles:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Managers can only create inhouse_sales, marketing, tele_calling for their own tenant
        if user.role == 'manager':
            role = request.data.get('role')
            if role not in ['inhouse_sales', 'marketing', 'tele_calling']:
                return Response({'detail': 'Managers can only add In-house Sales, Marketing, or Tele-calling users.'}, status=status.HTTP_403_FORBIDDEN)
            # Force the new user to have the same tenant as the manager
            request.data['tenant'] = user.tenant_id

        # Business admin can only create users for their own tenant
        if user.role == 'business_admin':
            request.data['tenant'] = user.tenant_id

        # Ensure user is active by default
        request.data['is_active'] = True

        response = super().create(request, *args, **kwargs)
        # Double-check and set is_active in case serializer ignores it
        if response.status_code == 201 and 'id' in response.data:
            try:
                created_user = User.objects.get(id=response.data['id'])
                if not created_user.is_active:
                    created_user.is_active = True
                    created_user.save()
            except Exception as e:
                print('Could not set user as active:', e)
        return response


class UserDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific user (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsRoleAllowed.for_roles(['platform_admin'])]


class UserUpdateView(generics.UpdateAPIView):
    """
    Update a specific user (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsRoleAllowed.for_roles(['platform_admin'])]


class UserDeleteView(generics.DestroyAPIView):
    """
    Delete a specific user (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsRoleAllowed.for_roles(['platform_admin'])]


# Team Member Views
class TeamMemberListView(generics.ListCreateAPIView):
    """
    List and create team members.
    """
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for different operations."""
        if self.request.method == 'GET':
            return TeamMemberListSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return TeamMemberUpdateSerializer
        elif self.request.method == 'POST':
            return TeamMemberCreateSerializer
        return TeamMemberSerializer

    def get_queryset(self):
        """Filter team members based on user's role, tenant, and store."""
        user = self.request.user
        queryset = TeamMember.objects.all()

        if user.is_platform_admin:
            pass
        elif user.is_business_admin and user.tenant:
            queryset = queryset.filter(user__tenant=user.tenant)
        elif user.is_manager:
            queryset = queryset.filter(Q(user=user) | Q(manager__user=user))
        elif user.role == 'tele_caller' and user.tenant and user.store:
            queryset = queryset.filter(user__tenant=user.tenant, user__store=user.store, user__role='tele_caller')
        else:
            queryset = queryset.filter(user=user)

        store_id = self.request.query_params.get('store')
        if store_id:
            queryset = queryset.filter(user__store_id=store_id)

        return queryset


    def perform_create(self, serializer):
        """Set tenant for new team members."""
        team_member = serializer.save()
        
        # Set tenant based on current user
        if self.request.user.tenant:
            team_member.user.tenant = self.request.user.tenant
            team_member.user.save()
        
        # Log activity
        TeamMemberActivity.objects.create(
            team_member=team_member,
            activity_type='task_completed',
            description=f'Team member {team_member.user.get_full_name()} was added to the team'
        )


class TeamMemberCreateView(generics.CreateAPIView):
    """
    Create a new team member.
    """
    serializer_class = TeamMemberCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # Restrict manager to only create certain roles
        if user.role == 'manager':
            role = self.request.data.get('role')
            if role not in ['inhouse_sales', 'marketing', 'tele_calling']:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Managers can only add In-house Sales, Marketing, or Tele-calling users.")

            # Set manager field to self if not provided
            if not self.request.data.get('manager'):
                try:
                    manager_tm = TeamMember.objects.get(user=user)
                    serializer.validated_data['manager'] = manager_tm
                except TeamMember.DoesNotExist:
                    pass

        team_member = serializer.save()
        # Set tenant based on current user
        if user.tenant:
            team_member.user.tenant = user.tenant
            team_member.user.save()
        # Update manager if provided
        manager_id = self.request.data.get('manager')
        if manager_id:
            try:
                manager = TeamMember.objects.get(id=manager_id, user__tenant=user.tenant)
                team_member.manager = manager
                team_member.save()
            except TeamMember.DoesNotExist:
                pass


class TeamMemberUpdateView(generics.UpdateAPIView):
    """
    Update a team member.
    """
    serializer_class = TeamMemberUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter team members based on user's role and tenant."""
        user = self.request.user
        
        if user.is_platform_admin:
            return TeamMember.objects.all()
        
        if user.is_business_admin and user.tenant:
            return TeamMember.objects.filter(user__tenant=user.tenant)
        
        if user.is_manager:
            return TeamMember.objects.filter(
                Q(user=user) | Q(manager__user=user)
            )
        
        return TeamMember.objects.filter(user=user)

    def perform_update(self, serializer):
        """Log activity when team member is updated."""
        team_member = serializer.save()
        
        TeamMemberActivity.objects.create(
            team_member=team_member,
            activity_type='task_completed',
            description=f'Team member {team_member.user.get_full_name()} profile was updated'
        )


class TeamMemberDeleteView(generics.DestroyAPIView):
    """
    Delete a team member.
    """
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter team members based on user's role and tenant."""
        user = self.request.user
        
        if user.is_platform_admin:
            return TeamMember.objects.all()
        
        if user.is_business_admin and user.tenant:
            return TeamMember.objects.filter(user__tenant=user.tenant)
        
        if user.is_manager:
            return TeamMember.objects.filter(
                Q(user=user) | Q(manager__user=user)
            )
        
        return TeamMember.objects.filter(user=user)

    def perform_destroy(self, instance):
        """Log activity when team member is removed."""
        user_name = instance.user.get_full_name()
        user_id = instance.user.id
        
        # Delete the team member (this will cascade to delete the user)
        instance.delete()


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete team members.
    """
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return TeamMemberUpdateSerializer
        return TeamMemberSerializer

    def get_queryset(self):
        """Filter team members based on user's role and tenant."""
        user = self.request.user
        
        if user.is_platform_admin:
            return TeamMember.objects.all()
        
        if user.is_business_admin and user.tenant:
            return TeamMember.objects.filter(user__tenant=user.tenant)
        
        if user.is_manager:
            return TeamMember.objects.filter(
                Q(user=user) | Q(manager__user=user)
            )
        
        return TeamMember.objects.filter(user=user)

    def perform_update(self, serializer):
        """Log activity when team member is updated."""
        team_member = serializer.save()
        
        TeamMemberActivity.objects.create(
            team_member=team_member,
            activity_type='task_completed',
            description=f'Team member {team_member.user.get_full_name()} profile was updated'
        )
    
    def update(self, request, *args, **kwargs):
        """Override update method to add debugging."""
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            print(f"Update error: {e}")
            raise

    def perform_destroy(self, instance):
        """Log activity when team member is removed."""
        user_name = instance.user.get_full_name()
        user_id = instance.user.id
        
        # Delete the team member (this will cascade to delete the user)
        instance.delete()
        
        # Note: We can't log activity after deletion since the team_member is gone
        # The activity logging is handled by the cascade delete in the model


class TeamMemberActivityView(generics.ListCreateAPIView):
    """
    List and create team member activities.
    """
    serializer_class = TeamMemberActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter activities based on user's permissions."""
        user = self.request.user
        
        if user.is_platform_admin:
            return TeamMemberActivity.objects.all()
        
        if user.is_business_admin and user.tenant:
            return TeamMemberActivity.objects.filter(
                team_member__user__tenant=user.tenant
            )
        
        if user.is_manager:
            return TeamMemberActivity.objects.filter(
                Q(team_member__user=user) | Q(team_member__manager__user=user)
            )
        
        return TeamMemberActivity.objects.filter(team_member__user=user)

    def perform_create(self, serializer):
        """Create activity and update last login if it's a login activity."""
        activity = serializer.save()
        
        if activity.activity_type == 'login':
            activity.team_member.user.last_login = timezone.now()
            activity.team_member.user.save()


class TeamMemberPerformanceView(generics.ListCreateAPIView):
    """
    List and create team member performance records.
    """
    serializer_class = TeamMemberPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter performance records based on user's permissions."""
        user = self.request.user
        
        if user.is_platform_admin:
            return TeamMemberPerformance.objects.all()
        
        if user.is_business_admin and user.tenant:
            return TeamMemberPerformance.objects.filter(
                team_member__user__tenant=user.tenant
            )
        
        if user.is_manager:
            return TeamMemberPerformance.objects.filter(
                Q(team_member__user=user) | Q(team_member__manager__user=user)
            )
        
        return TeamMemberPerformance.objects.filter(team_member__user=user)


class TeamStatsView(APIView):
    """
    Get team statistics and analytics.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Calculate and return team statistics."""
        user = request.user
        
        # Get base queryset based on user permissions
        if user.is_platform_admin:
            team_members = TeamMember.objects.all()
        elif user.is_business_admin and user.tenant:
            team_members = TeamMember.objects.filter(user__tenant=user.tenant)
        elif user.is_manager:
            team_members = TeamMember.objects.filter(
                Q(user=user) | Q(manager__user=user)
            )
        else:
            team_members = TeamMember.objects.filter(user=user)
        
        # Calculate statistics
        total_members = team_members.count()
        active_members = team_members.filter(status='active').count()
        total_sales = team_members.aggregate(
            total=Sum('current_sales')
        )['total'] or 0
        
        # Calculate average performance
        performance_ratings = {
            'excellent': 5,
            'good': 4,
            'average': 3,
            'below_average': 2,
            'poor': 1
        }
        
        avg_performance = 0
        if total_members > 0:
            total_rating = 0
            for member in team_members:
                if member.performance_rating:
                    total_rating += performance_ratings.get(member.performance_rating, 3)
            avg_performance = total_rating / total_members
        
        # Get top performers
        top_performers = team_members.filter(
            performance_rating__in=['excellent', 'good']
        ).order_by('-current_sales')[:5]
        
        top_performers_data = []
        for member in top_performers:
            top_performers_data.append({
                'id': member.id,
                'name': member.user.get_full_name(),
                'role': member.user.get_role_display(),
                'sales': float(member.current_sales),
                'performance': member.performance_rating
            })
        
        # Get recent activities
        recent_activities = TeamMemberActivity.objects.filter(
            team_member__in=team_members
        ).order_by('-created_at')[:10]
        
        recent_activities_data = []
        for activity in recent_activities:
            recent_activities_data.append({
                'id': activity.id,
                'member_name': activity.team_member.user.get_full_name(),
                'activity_type': activity.get_activity_type_display(),
                'description': activity.description,
                'created_at': activity.created_at.isoformat()
            })
        
        # Prepare response data
        stats_data = {
            'total_members': total_members,
            'active_members': active_members,
            'total_sales': float(total_sales),
            'avg_performance': round(avg_performance, 2),
            'top_performers': top_performers_data,
            'recent_activities': recent_activities_data
        }
        
        serializer = TeamStatsSerializer(stats_data)
        return Response(serializer.data)


class TeamMemberSearchView(generics.ListAPIView):
    """
    Search team members by name, email, or role.
    """
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = TeamMember.objects.all()

        # Filter by tenant
        if user.tenant:
            queryset = queryset.filter(user__tenant=user.tenant)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__role__icontains=search)
            )

        return queryset


class MessagingUsersView(generics.ListAPIView):
    """
    Get all users in the same tenant for messaging purposes.
    Returns user data in the format expected by the frontend.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        print(f"[MessagingUsersView] Current user: {user.username}, tenant: {user.tenant}")
        
        queryset = User.objects.filter(is_active=True)
        print(f"[MessagingUsersView] Initial queryset count: {queryset.count()}")
        
        # Filter by tenant
        if user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
            print(f"[MessagingUsersView] After tenant filter count: {queryset.count()}")
        
        # Exclude the current user from the list
        queryset = queryset.exclude(id=user.id)
        print(f"[MessagingUsersView] After excluding current user count: {queryset.count()}")
        
        # Print some sample users
        sample_users = list(queryset[:3].values('username', 'first_name', 'last_name', 'role'))
        print(f"[MessagingUsersView] Sample users: {sample_users}")
        
        return queryset
    
    def get_serializer_class(self):
        return MessagingUserSerializer


class ManagerDashboardView(APIView):
    """
    Manager dashboard view providing overview data for managers.
    """
    permission_classes = [IsRoleAllowed.for_roles(['manager'])]

    def get(self, request):
        """Get manager dashboard data."""
        user = request.user
        
        # Check if user is authenticated
        if not user.is_authenticated:
            return Response({
                'error': 'Authentication required. Please log in.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Ensure user is a manager
        if not hasattr(user, 'is_manager') or not user.is_manager:
            return Response({
                'error': 'Access denied. Only managers can access this dashboard.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Get team members under this manager (if any)
            team_members = TeamMember.objects.filter(manager__user=user)
            total_team_members = team_members.count()
            active_members = team_members.filter(status='active').count()
            
            # Calculate total sales for the team
            total_team_sales = team_members.aggregate(
                total=Sum('current_sales')
            )['total'] or 0
            
            # Get recent activities (if any)
            recent_activities = TeamMemberActivity.objects.filter(
                team_member__in=team_members
            ).order_by('-created_at')[:5]
            
            # Get performance summary
            performance_summary = {
                'excellent': team_members.filter(performance_rating='excellent').count(),
                'good': team_members.filter(performance_rating='good').count(),
                'average': team_members.filter(performance_rating='average').count(),
                'below_average': team_members.filter(performance_rating='below_average').count(),
                'poor': team_members.filter(performance_rating='poor').count(),
            }
            
            # Get basic store statistics
            from apps.clients.models import Client
            from apps.escalation.models import Escalation
            
            # Get clients assigned to users in this manager's store
            if user.store:
                store_clients = Client.objects.filter(assigned_to__store=user.store)
                
                # Count leads (clients with no purchases)
                total_leads = store_clients.filter(purchases__isnull=True).distinct().count()
                
                # Count customers (clients with purchases)
                total_customers = store_clients.filter(purchases__isnull=False).distinct().count()
                
                # Count total sales (sum of all purchases)
                total_sales = store_clients.aggregate(
                    total_sales=Sum('purchases__amount')
                )['total_sales'] or 0
            else:
                total_leads = 0
                total_customers = 0
                total_sales = 0
            
            # Get escalations for this store
            if user.store:
                store_escalations = Escalation.objects.filter(
                    client__assigned_to__store=user.store
                )
                total_tasks = store_escalations.filter(status__in=['open', 'in_progress']).count()
            else:
                total_tasks = 0
            
            # Prepare response data
            dashboard_data = {
                'teamMembers': total_team_members,
                'leads': total_leads,
                'sales': float(total_sales),
                'tasks': total_tasks,
                'total_team_members': total_team_members,
                'active_members': active_members,
                'total_team_sales': float(total_team_sales),
                'performance_summary': performance_summary,
                'recent_activities': [
                    {
                        'id': activity.id,
                        'member_name': activity.team_member.user.get_full_name(),
                        'activity_type': activity.get_activity_type_display(),
                        'description': activity.description,
                        'created_at': activity.created_at.isoformat()
                    }
                    for activity in recent_activities
                ]
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            return Response({
                'error': f'Error loading dashboard data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



