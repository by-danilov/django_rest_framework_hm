from django.db import models
from django.contrib.auth.models import AbstractUser
from lms.models import Course, Lesson

class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return self.email


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField()
    paid_course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL, related_name='course_payments')
    paid_lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL, related_name='lesson_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=[('cash', 'Наличные'), ('transfer', 'Перевод на счёт')]
    )

    class Meta:
        db_table = 'payments'
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Платёж от {self.user.email} на сумму {self.amount}"