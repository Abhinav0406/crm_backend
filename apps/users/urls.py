from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # User Management (Admin only)
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('create/', views.UserCreateView.as_view(), name='user-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    
    # Team Member Management
    path('team-members/', views.TeamMemberListView.as_view(), name='team-member-list'),
    path('team-members/create/', views.TeamMemberCreateView.as_view(), name='team-member-create'),
    path('team-members/search/', views.TeamMemberSearchView.as_view(), name='team-member-search'),
    path('team-members/<int:pk>/', views.TeamMemberDetailView.as_view(), name='team-member-detail'),
    path('team-members/<int:pk>/update/', views.TeamMemberUpdateView.as_view(), name='team-member-update'),
    path('team-members/<int:pk>/delete/', views.TeamMemberDeleteView.as_view(), name='team-member-delete'),
    
    # Team Member Activities
    path('team-members/activities/', views.TeamMemberActivityView.as_view(), name='team-member-activities'),
    path('team-members/<int:pk>/activities/', views.TeamMemberActivityView.as_view(), name='team-member-activities-detail'),
    
    # Team Member Performance
    path('team-members/performance/', views.TeamMemberPerformanceView.as_view(), name='team-member-performance'),
    path('team-members/<int:pk>/performance/', views.TeamMemberPerformanceView.as_view(), name='team-member-performance-detail'),
    
    # Team Statistics
    path('team-stats/', views.TeamStatsView.as_view(), name='team-stats'),
    path('managers/dashboard/', views.ManagerDashboardView.as_view(), name='manager-dashboard'),
    
    # Messaging users
    path('messaging-users/', views.MessagingUsersView.as_view(), name='messaging-users'),
] 