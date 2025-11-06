from rest_framework import viewsets, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsModeratorOrOwner


def is_moderator(user):
    """Вспомогательная функция (дублируется из users.permissions для автономности)."""
    return user.groups.filter(name='Модераторы').exists()

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [IsModeratorOrOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if is_moderator(self.request.user):
            return Course.objects.all()
        return Course.objects.filter(user=self.request.user)



class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [IsModeratorOrOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if is_moderator(self.request.user):
            return Lesson.objects.all()
        return Lesson.objects.filter(user=self.request.user)
