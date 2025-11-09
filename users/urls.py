from django.urls import path
from .views import register, login, UserDetailView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]
