from rest_framework import serializers
from .models import Level, Employee, Evaluation, Objective


# ========================
# LEVEL SERIALIZER
# ========================
class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


# ========================
# EMPLOYEE SERIALIZER
# ========================
class EmployeeSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.name', read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'name',
            'position',
            'department',
            'level',
            'level_name',
            'manager',
            'manager_name',
        ]


# ========================
# OBJECTIVE SERIALIZER
# ========================
class ObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objective
        fields = '__all__'


# ========================
# EVALUATION SERIALIZER
# ========================
class EvaluationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    # 🔥 Nested objectives (IMPORTANT)
    objectives = ObjectiveSerializer(many=True)

    class Meta:
        model = Evaluation
        fields = [
            'id',
            'employee',
            'employee_name',
            'performance_period',
            'employee_comment',
            'manager_comment',
            'date_completed',
            'objectives',
        ]

    # ========================
    # CREATE (with objectives)
    # ========================
    def create(self, validated_data):
        objectives_data = validated_data.pop('objectives')
        evaluation = Evaluation.objects.create(**validated_data)

        for obj_data in objectives_data:
            Objective.objects.create(evaluation=evaluation, **obj_data)

        return evaluation

    # ========================
    # UPDATE (optional basic)
    # ========================
    def update(self, instance, validated_data):
        objectives_data = validated_data.pop('objectives', None)

        instance.employee = validated_data.get('employee', instance.employee)
        instance.performance_period = validated_data.get('performance_period', instance.performance_period)
        instance.employee_comment = validated_data.get('employee_comment', instance.employee_comment)
        instance.manager_comment = validated_data.get('manager_comment', instance.manager_comment)
        instance.date_completed = validated_data.get('date_completed', instance.date_completed)

        instance.save()

        # simple replace strategy
        if objectives_data is not None:
            instance.objectives.all().delete()
            for obj_data in objectives_data:
                Objective.objects.create(evaluation=instance, **obj_data)

        return instance