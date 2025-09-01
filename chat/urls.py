from django.urls import path
from .views import (
    chat,
    start_tutoring_session,
    tutoring_chat,
    generate_exam,
    submit_exam,
    get_learning_path,
    get_session_progress,
    get_user_profile,
    explain_concept,
    get_exam_results
)

urlpatterns = [
    # Original chat endpoint (backwards compatibility)
    path('chat/', chat, name='chat'),
    
    # Tutoring endpoints
    path('tutoring/start/', start_tutoring_session, name='start_tutoring'),
    path('tutoring/chat/', tutoring_chat, name='tutoring_chat'),
    path('tutoring/session/<str:session_id>/progress/', get_session_progress, name='session_progress'),
    
    # Exam endpoints
    path('exam/generate/', generate_exam, name='generate_exam'),
    path('exam/submit/', submit_exam, name='submit_exam'),
    path('exam/<str:exam_id>/results/', get_exam_results, name='exam_results'),
    
    # Learning support endpoints
    path('learning/path/', get_learning_path, name='learning_path'),
    path('learning/explain/', explain_concept, name='explain_concept'),
    
    # User profile endpoint
    path('user/<str:user_id>/profile/', get_user_profile, name='user_profile'),
]