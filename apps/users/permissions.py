from rest_framework.permissions import BasePermission

class IsRoleAllowed(BasePermission):
    """
    Allows access only to users with specified roles.
    Usage: IsRoleAllowed(['platform_admin', 'manager'])
    """
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # If allowed_roles is set on the view, use that
        allowed_roles = getattr(view, 'allowed_roles', self.allowed_roles)
        return user.role in allowed_roles

    @classmethod
    def for_roles(cls, allowed_roles):
        # Helper to use in permission_classes: IsRoleAllowed.for_roles(['role1', 'role2'])
        class _IsRoleAllowed(cls):
            def __init__(self):
                super().__init__(allowed_roles)
        return _IsRoleAllowed


class IsManagerOrHigher(BasePermission):
    """
    Allows access only to managers and higher roles.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in ['platform_admin', 'business_admin', 'manager']


class IsBusinessAdminOrHigher(BasePermission):
    """
    Allows access only to business admins and higher roles.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in ['platform_admin', 'business_admin'] 