from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Course, Lesson
from users.models import CourseSubscription


User = get_user_model()

class LessonCRUDTests(APITestCase):
    def setUp(self):
        # Создаём пользователя
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            phone='1234567890',
            city='Moscow'
        )
        # Авторизуем клиента
        self.client.force_authenticate(user=self.user)

        # Создаём курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Description'
        )

    def test_create_lesson(self):
        url = '/api/lessons/'
        data = {
            'course': self.course.id,
            'title': 'Test Lesson',
            'description': 'Lesson description',
            'video_url': 'https://youtube.com/watch?v=abc'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_retrieve_lesson(self):
        lesson = Lesson.objects.create(
            course=self.course,
            title='Lesson 1',
            video_url='https://youtube.com/watch?v=def'
        )
        url = f'/api/lessons/{lesson.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Lesson 1')

    def test_update_lesson(self):
        lesson = Lesson.objects.create(
            course=self.course,
            title='Old Title',
            video_url='https://youtube.com/watch?v=ghi'
        )
        url = f'/api/lessons/{lesson.id}/'
        data = {'title': 'Updated Title', 'video_url': 'https://youtube.com/watch?v=jkl'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_delete_lesson(self):
        lesson = Lesson.objects.create(
            course=self.course,
            title='To Delete',
            video_url='https://youtube.com/watch?v=mno'
        )
        url = f'/api/lessons/{lesson.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='sub@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(title='Sub Course')

    def test_subscribe(self):
        url = f'/api/courses/{self.course.id}/subscribe/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseSubscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        subscription = CourseSubscription.objects.create(user=self.user, course=self.course)
        url = f'/api/courses/{self.course.id}/unsubscribe/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            CourseSubscription.objects.filter(id=subscription.id).exists()
        )

    def test_is_subscribed_in_course_detail(self):
        CourseSubscription.objects.create(user=self.user, course=self.course)
        url = f'/api/courses/{self.course.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])
