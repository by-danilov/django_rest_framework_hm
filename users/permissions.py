from rest_framework import permissions

def is_moderator(user):
    """Проверяет, входит ли пользователь в группу «Модераторы»."""
    return user.groups.filter(name='Модераторы').exists()

class IsModerator(permissions.BasePermission):
    """
    Разрешает доступ только пользователям из группы «Модераторы».
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            is_moderator(request.user)
        )

class IsModeratorOrOwner(permissions.BasePermission):
    """
    Разрешает:
    - Модераторам — полный доступ к любому объекту.
    - Владельцу объекта — доступ к своему объекту.
    """
    def has_object_permission(self, request, view, obj):
        if is_moderator(request.user):
            return True
        return obj.user == request.user
