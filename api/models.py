from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# ========================
# LEVELS (with percentages)
# ========================
class Level(models.Model):
    name = models.CharField(max_length=100, unique=True)
    company_percentage = models.IntegerField()
    individual_percentage = models.IntegerField()

    def __str__(self):
        return self.name


# ========================
# EMPLOYEES
# ========================
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    department = models.CharField(max_length=150)

    level = models.ForeignKey(Level, on_delete=models.PROTECT)

    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# ========================
# EVALUATION
# ========================
class Evaluation(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="evaluations"
    )
    performance_period = models.CharField(max_length=100)

    employee_comment = models.TextField(blank=True, null=True)
    manager_comment = models.TextField(blank=True, null=True)

    date_completed = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'performance_period')

    def __str__(self):
        return f"{self.employee.name} - {self.performance_period}"


# ========================
# OBJECTIVES
# ========================
class Objective(models.Model):
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name="objectives"
    )

    order = models.IntegerField(default=1)

    description = models.TextField()

    due_when = models.DateField(null=True, blank=True)

    weight = models.FloatField()

    measure = models.CharField(max_length=255)
    target = models.CharField(max_length=255)

    employee_actual = models.FloatField(null=True, blank=True)
    manager_actual = models.FloatField(null=True, blank=True)

    score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ('evaluation', 'order')

    def clean(self):
        if self.employee_actual is not None and self.employee_actual > 110:
            raise ValidationError("Employee actual cannot exceed 110%")

        if self.manager_actual is not None and self.manager_actual > 110:
            raise ValidationError("Manager actual cannot exceed 110%")

        if self.weight < 0:
            raise ValidationError("Weight cannot be negative")

    def save(self, *args, **kwargs):
        # 🔥 compute score if manager_actual exists
        if self.manager_actual is not None:
            self.score = (self.manager_actual / 100) * self.weight

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description