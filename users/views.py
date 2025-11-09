from rest_framework import views, permissions, viewsets, generics
from django_filters import rest_framework as filters
from .serializers import PaymentSerializer
from .models import Payment
from .permissions import IsModeratorOrOwner, IsModerator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CourseSubscription, Course


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'course': ['exact'],
        'lesson': ['exact'],
        'payment_method': ['exact'],
        'payment_date': ['gte', 'lte', 'exact'],
    }
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

class CourseViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        course = self.get_object()
        subscription, created = CourseSubscription.objects.get_or_create(
            user=request.user,
            course=course
        )
        if created:
            return Response({'status': 'подписан'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'уже подписан'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        course = self.get_object()
        try:
            subscription = CourseSubscription.objects.get(
                user=request.user,
                course=course
            )
            subscription.delete()
            return Response({'status': 'отписан'}, status=status.HTTP_204_NO_CONTENT)
        except CourseSubscription.DoesNotExist:
            return Response({'error': 'подписки нет'}, status=status.HTTP_404_NOT_FOUND)