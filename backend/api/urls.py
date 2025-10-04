from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet, UserCreateAPIView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('', include(router.urls)),
]
