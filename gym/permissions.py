from rest_framework import permissions

class HasActiveSubscription(permissions.BasePermission):
    """
    Custom permission to only allow members with active subscriptions.
    """
    message = "Your subscription has expired. Please renew your subscription to continue."

    def has_permission(self, request, view):
        # Allow unauthenticated requests to pass (they'll be handled by other permission classes)
        if not request.user or not request.user.is_authenticated:
            return True
            
        # Always allow admin/staff users
        if request.user.is_staff:
            return True
            
        # For regular members, check subscription status
        try:
            member = request.user
            return member.has_active_subscription
        except:
            return False