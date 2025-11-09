from rest_framework import views, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters import rest_framework as filters
from .serializers import UserSerializer, PaymentSerializer
from .models import Payment
from .permissions import IsModeratorOrOwner, IsModerator



class RegisterView(views.APIView):
    """
    Регистрация нового пользователя.
    Возвращает JWT-токены (access и refresh) после успешного создания.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PaymentViewSet(viewsets.ModelViewSet):
    """
    API для управления платежами.
    - Модераторы видят все платежи.
    - Обычные пользователи видят только свои.
    - Создание/редактирование доступно авторизованным.
    - Удаление — только админам.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [IsModeratorOrOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Модераторы видят все платежи, остальные — только свои
        if IsModerator().has_permission(self.request, self):
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Автоматически привязываем текущего пользователя как владельца платежа
        serializer.save(user=self.request.user)
