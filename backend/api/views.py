from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Quiz, Question, Choice, Enrollment, Progress
from .serializers import (
    CourseSerializer, LessonSerializer, UserCreateSerializer, UserProgressSerializer,
    QuizSerializer, QuestionSerializer, ChoiceSerializer, EnrollmentSerializer
)
from .permissions import IsInstructorOrReadOnly

# --- User & Auth Views ---
class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

# --- Course & Lesson Views with Actions ---
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsInstructorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, 
            course=course
        )
        if not created:
            return Response({'detail': 'Already enrolled.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsInstructorOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        # Check if user is enrolled in the course this lesson belongs to
        if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
            return Response({'detail': 'Not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN)
            
        progress, _ = Progress.objects.get_or_create(student=request.user, lesson=lesson)
        progress.is_completed = True
        progress.save()
        return Response({'status': 'Lesson marked as complete.'})

# --- Quiz & Question Views ---
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        user_answers = request.data.get('answers', []) # Expects: [{"question_id": 1, "choice_id": 3}]
        
        score = 0
        total_questions = quiz.questions.count()

        for answer in user_answers:
            try:
                choice = Choice.objects.get(id=answer.get('choice_id'), question_id=answer.get('question_id'))
                if choice.is_correct:
                    score += 1
            except Choice.DoesNotExist:
                continue # Ignore invalid answers

        return Response({
            'score': score,
            'total': total_questions,
        })

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrReadOnly]

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrReadOnly]

# --- User Progress View ---
class UserProgressView(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)
