from django.urls import path
from .views import (
    LevelListAPIView,
    EmployeeListAPIView,
    EvaluationListCreateAPIView,
    EvaluationRetrieveUpdateDestroyAPIView,
    ObjectiveListAPIView,
)

urlpatterns = [
    path('levels/', LevelListAPIView.as_view()),
    path('employees/', EmployeeListAPIView.as_view()),
    path('evaluations/', EvaluationListCreateAPIView.as_view()),
    path('evaluations/<int:pk>/', EvaluationRetrieveUpdateDestroyAPIView.as_view()),
    path('objectives/', ObjectiveListAPIView.as_view()),
]