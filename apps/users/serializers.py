from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, TeamMember, TeamMemberActivity, TeamMemberPerformance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    store_name = serializers.SerializerMethodField()
    store = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone', 'address', 'profile_picture', 'tenant', 'is_active',
            'created_at', 'updated_at', 'last_login',
            'store', 'store_name',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']

    def get_store_name(self, obj):
        return obj.store.name if obj.store else None


class MessagingUserSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for messaging users.
    Only includes essential fields needed for the frontend.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 'address'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    """
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    dashboard_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone', 'address', 'profile_picture', 'tenant', 'dashboard_url'
        ]
        read_only_fields = ['id', 'username', 'tenant', 'role', 'dashboard_url']
    
    def get_dashboard_url(self, obj):
        """Return the appropriate dashboard URL based on user role."""
        role_dashboard_map = {
            'platform_admin': '/platform-admin/dashboard',
            'business_admin': '/business-admin/dashboard',
            'manager': '/managers/dashboard',
            'inhouse_sales': '/inhouse-sales/dashboard',
            'tele_calling': '/tele-calling/dashboard',
            'marketing': '/marketing/dashboard',
        }
        return role_dashboard_map.get(obj.role, '/dashboard')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class TeamMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for TeamMember model.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)
    sales_percentage = serializers.ReadOnlyField()
    is_performing_well = serializers.ReadOnlyField()
    performance_color = serializers.ReadOnlyField()

    class Meta:
        model = TeamMember
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'department', 'position',
            'hire_date', 'status', 'performance_rating', 'sales_target',
            'current_sales', 'manager', 'manager_name', 'skills', 'notes',
            'sales_percentage', 'is_performing_well', 'performance_color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at']

    def validate_user_id(self, value):
        """Validate that the user exists and is not already a team member."""
        try:
            user = User.objects.get(id=value)
            if hasattr(user, 'team_member'):
                raise serializers.ValidationError("User is already a team member")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        team_member = TeamMember.objects.create(user=user, **validated_data)
        return team_member


class TeamMemberListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for team member lists.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.get_role_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    sales_percentage = serializers.ReadOnlyField()
    performance_color = serializers.ReadOnlyField()
    store_name = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = [
            'id', 'employee_id', 'user_name', 'user_email', 'user_role',
            'user_username', 'department', 'position', 'status',
            'performance_rating', 'sales_target', 'current_sales',
            'sales_percentage', 'performance_color', 'hire_date',
            'store_name',
        ]

    def get_store_name(self, obj):
        return obj.user.store.name if obj.user and obj.user.store else None


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating team members with user data.
    """
    # User fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    role = serializers.ChoiceField(choices=User.Role.choices)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    store = serializers.PrimaryKeyRelatedField(queryset=User._meta.get_field('store').related_model.objects.all(), required=False, allow_null=True)
    
    # Team member fields
    department = serializers.CharField(max_length=50, required=False, allow_blank=True)
    position = serializers.CharField(max_length=100, required=False, allow_blank=True)
    hire_date = serializers.DateField(required=False)
    sales_target = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = TeamMember
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone', 'department', 'position', 'hire_date',
            'sales_target', 'manager_id', 'skills', 'notes',
            'store',
        ]

    def validate_username(self, value):
        """Check that username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Check that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_manager_id(self, value):
        """Validate manager exists and is a team member."""
        if value is not None:
            try:
                manager = TeamMember.objects.get(id=value)
                return value
            except TeamMember.DoesNotExist:
                raise serializers.ValidationError("Manager does not exist")
        return value

    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'role': validated_data.pop('role'),
            'phone': validated_data.pop('phone', ''),
            'is_active': True,  # Ensure user is active
            'store': validated_data.pop('store', None),
        }
        password = validated_data.pop('password')
        
        # Extract team member data
        manager_id = validated_data.pop('manager_id', None)
        
        # Create user
        user = User(**user_data)
        user.set_password(password)
        user.save()
        
        # Set manager if provided
        if manager_id:
            validated_data['manager_id'] = manager_id
        
        # Create team member
        team_member = TeamMember.objects.create(user=user, **validated_data)
        
        return team_member


class TeamMemberUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating team members.
    """
    # User fields that can be updated (without source to handle flat data)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)
    
    # Team member fields
    department = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    hire_date = serializers.DateField(required=False)
    status = serializers.ChoiceField(choices=TeamMember.Status.choices, required=False)
    performance_rating = serializers.ChoiceField(choices=TeamMember.Performance.choices, required=False)
    sales_target = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = TeamMember
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'role',
            'department', 'position', 'hire_date', 'status', 'performance_rating',
            'sales_target', 'skills', 'notes'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        """Check that email is unique if changed."""
        if value and User.objects.filter(email=value).exclude(id=self.instance.user.id).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def update(self, instance, validated_data):
        # Update user fields
        user_data = {}
        for field in ['first_name', 'last_name', 'email', 'phone', 'role']:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        if user_data:
            for field, value in user_data.items():
                setattr(instance.user, field, value)
            instance.user.save()
        
        # Update team member fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()
        return instance


class TeamMemberActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for team member activities.
    """
    team_member_name = serializers.CharField(source='team_member.user.get_full_name', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = TeamMemberActivity
        fields = [
            'id', 'team_member', 'team_member_name', 'activity_type',
            'activity_type_display', 'description', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TeamMemberPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for team member performance records.
    """
    team_member_name = serializers.CharField(source='team_member.user.get_full_name', read_only=True)
    sales_percentage = serializers.ReadOnlyField()
    conversion_rate = serializers.ReadOnlyField()

    class Meta:
        model = TeamMemberPerformance
        fields = [
            'id', 'team_member', 'team_member_name', 'month', 'sales_target',
            'actual_sales', 'leads_generated', 'deals_closed',
            'customer_satisfaction', 'notes', 'sales_percentage',
            'conversion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeamStatsSerializer(serializers.Serializer):
    """
    Serializer for team statistics.
    """
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_performance = serializers.DecimalField(max_digits=5, decimal_places=2)
    top_performers = serializers.ListField()
    recent_activities = serializers.ListField() 