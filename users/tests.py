from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Course, Lesson, CourseSubscription
from .serializers import CourseSerializer, LessonSerializer

class LessonsAndSubscriptionsTests(APITestCase):
    def setUp(self):
        # Создаём пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123',
            email='user2@example.com'
        )

        # Создаём курс и урок
        self.course = Course.objects.create(
            title='Тест-курс',
            description='Описание курса'
        )
        self.lesson = Lesson.objects.create(
            title='Урок 1',
            content='Контент урока',
            course=self.course
        )

        # Клиент для аутентифицированных запросов
        self.client = APIClient()

    # Тесты CRUD для уроков (Lesson)
    def test_create_lesson_as_authenticated(self):
        """Тест создания урока аутентифицированным пользователем."""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Новый урок',
            'content': 'Контент',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_unauthenticated(self):
        """Тест попытки создания урока неавторизованным пользователем."""
        data = {
            'title': 'Урок без авторизации',
            'content': 'Контент',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_lessons_list(self):
        """Тест получения списка уроков."""
        response = self.client.get('/api/lessons/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Учитываем пагинацию

    def test_get_lesson_detail(self):
        """Тест получения детальной информации об уроке."""
        response = self.client.get(f'/api/lessons/{self.lesson.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Урок 1')

    def test_update_lesson(self):
        """Тест обновления урока аутентифицированным пользователем."""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Обновлённый урок',
            'content': 'Обновлённый контент',
            'course': self.course.id
        }
        response = self.client.put(f'/api/lessons/{self.lesson.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновлённый урок')

    def test_delete_lesson(self):
        """Тест удаления урока аутентифицированным пользователем."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    # Тесты функционала подписки на курс
    def test_subscribe_to_course(self):
        """Тест подписки пользователя на курс."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/', format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CourseSubscription.objects.filter(user=self.user1, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Тест отписки пользователя от курса."""
        # Сначала подписываемся
        self.client.force_authenticate(user=self.user1)
        self.client.post(f'/api/courses/{self.course.id}/subscribe/', format='json')

        # Затем отписываемся
        response = self.client.delete(f'/api/courses/{self.course.id}/unsubscribe/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseSubscription.objects.filter(user=self.user1, course=self.course).exists())

    def test_subscribe_already_subscribed(self):
        """Тест попытки подписаться на курс, на который уже подписаны."""
        self.client.force_authenticate(user=self.user1)
        # Сначала подписываемся
        self.client.post(f'/api/courses/{self.course.id}/subscribe/', format='json')
        # Пытаемся подписаться ещё раз
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_subscription_status_in_course_detail(self):
        """Тест проверки статуса подписки в деталях курса."""
        self.client.force_authenticate(user=self.user1)
        # Подписываемся
        self.client.post(f'/api/courses/{self.course.id}/subscribe/', format='json')
        # Получаем детали курса
        response = self.client.get(f'/api/courses/{self.course.id}/', format='json')
        self.assertEqual(response.data['is_subscribed'], True)

    def test_unauthenticated_subscription_attempt(self):
        """Тест попытки подписки неавторизованным пользователем."""
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
