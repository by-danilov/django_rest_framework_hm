from rest_framework import serializers
from .models import Course, Lesson
from .validators import YouTubeURLValidator
from users.models import CourseSubscription

class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[YouTubeURLValidator()])

    class Meta:
        model = Lesson
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseSubscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'preview',
            'lesson_count', 'lessons', 'is_subscribed'
        ]
