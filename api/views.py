from django.shortcuts import render
from rest_framework import generics
from .models import Level, Employee, Evaluation, Objective
from .serializers import (
    LevelSerializer,
    EmployeeSerializer,
    EvaluationSerializer,
    ObjectiveSerializer,
)


def home(request):
    return render(request, 'index.html')

def evaluation_page(request):
    return render(request, 'evaluation.html')
# ========================
# LEVELS
# ========================
class LevelListAPIView(generics.ListAPIView):
    queryset = Level.objects.all().order_by('id')
    serializer_class = LevelSerializer

# ========================
# EMPLOYEES
# ========================
class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.select_related('level', 'manager').all().order_by('name')
    serializer_class = EmployeeSerializer


# ========================
# EVALUATIONS (LIST + CREATE)
# ========================
class EvaluationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.select_related('employee').all().order_by('-id')
    serializer_class = EvaluationSerializer


# ========================
# EVALUATION DETAIL (UPDATE / DELETE)
# ========================
class EvaluationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer


# ========================
# OBJECTIVES (optional separate access)
# ========================
class ObjectiveListAPIView(generics.ListAPIView):
    queryset = Objective.objects.select_related('evaluation').all().order_by('order')
    serializer_class = ObjectiveSerializer
