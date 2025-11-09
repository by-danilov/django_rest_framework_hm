from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    def handle(self, *args, **options):
        content_type = ContentType.objects.get(app_label='courses', model='course')
        permission_names = [
            'view_course', 'change_course',
            'view_lesson', 'change_lesson',
        ]
        permissions = Permission.objects.filter(
            content_type=contenttype,
            codename__in=permission_names
        )
        moderator_group, _ = Group.objects.get_or_create(name='Модераторы')
        moderator_group.permissions.set(permissions)
        self.stdout.write('Группа "Модераторы" создана и права назначены.')
