from rest_framework import permissions

class IsModeratorOrOwner(permissions.BasePermission):
    """
    Разрешает:
    - Модераторам — просмотр и изменение любых курсов/уроков (без удаления и создания).
    - Владельцу объекта (если есть поле user) — полный CRUD.
    """
    def has_object_permission(self, request, view, obj):
        # Если пользователь в группе «Модераторы»
        if request.user.groups.filter(name='Модераторы').exists():
            # Модераторы могут только просматривать и изменять
            if request.method in ['GET', 'PUT', 'PATCH']:
                return True
            return False  # Запрет на DELETE и POST

        # Если объект принадлежит пользователю (предполагаем поле user)
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        return False
