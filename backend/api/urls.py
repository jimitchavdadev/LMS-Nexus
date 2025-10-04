from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, LessonViewSet, UserCreateAPIView, UserProgressView,
    QuizViewSet, QuestionViewSet, ChoiceViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('my-progress/', UserProgressView.as_view(), name='user-progress'),
    path('', include(router.urls)),
]
