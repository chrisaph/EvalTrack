from django.shortcuts import render
from rest_framework import generics
from .models import Level, Employee, Evaluation, Objective
from .serializers import (
    LevelSerializer,
    EmployeeSerializer,
    EvaluationSerializer,
    ObjectiveSerializer,
)
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            try:
                employee = user.employee
            except Employee.DoesNotExist:
                return render(request, "login.html", {
                    "error": "No employee profile linked"
                })

            # 🔥 CHECK IF MANAGER
            if Employee.objects.filter(manager=employee).exists():
                return redirect('/manager/')

            # otherwise normal employee
            return redirect('/evaluation/')

        else:
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

    # ✅ REQUIRED FOR GET REQUEST
    return render(request, "login.html")
def home(request):
    return render(request, 'index.html')

@login_required
def evaluation_page(request):
    employee = request.user.employee

    year = str(datetime.now().year - 1)

    evaluation = Evaluation.objects.filter(
        employee=employee,
        performance_period=year
    ).prefetch_related('objectives').first()

    return render(request, 'evaluation.html', {
        'employee': employee,
        'evaluation': evaluation,
        'year': year
    })
def manager_page(request):
    manager = request.user.employee

    employees = Employee.objects.filter(manager=manager)

    return render(request, 'manager.html', {
        'employees': employees
    })
def manager_evaluation_page(request, pk):
    manager = request.user.employee

    evaluation = Evaluation.objects.get(id=pk)

    # 🔥 SECURITY CHECK
    if evaluation.employee.manager != manager:
        return redirect('/manager/')

    return render(request, 'manager_evaluation.html', {
        'evaluation': evaluation
    })

def logout_view(request):
    logout(request)
    return redirect('/login/')
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
