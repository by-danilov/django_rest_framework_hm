from rest_framework import permissions

class IsModeratorOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_moderator(request.user):
            return True
        return obj.user == request.user
