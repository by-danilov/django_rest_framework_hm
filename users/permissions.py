from rest_framework import permissions

def is_moderator(user):
    return user.groups.filter(name='Модераторы').exists()

class IsModeratorOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_moderator(request.user):
            return True
        return obj.user == request.user
