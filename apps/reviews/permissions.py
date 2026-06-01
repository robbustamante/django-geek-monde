"""
Custom permissions for the reviews app.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Only allows the review author or admin users to edit/delete.
    Read access is allowed for everyone.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions only for the owner or admin
        return obj.author == request.user or request.user.is_staff
