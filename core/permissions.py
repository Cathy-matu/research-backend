from rest_framework import permissions

class IsDirectorOrDeputy(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['Director', 'Deputy Director']

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'Admin'

class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['Director', 'Deputy Director', 'Admin']:
            return True
        # For messages, check sender/receiver
        if hasattr(obj, 'sender'):
            return obj.sender == request.user or obj.receiver == request.user
        # For tasks, check assignee
        if hasattr(obj, 'assignee'):
            return obj.assignee == request.user
        # For events, check owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
