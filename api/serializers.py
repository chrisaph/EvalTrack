from rest_framework import serializers
from .models import Level, Employee, Evaluation, Objective
from django.utils import timezone

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
    level_company_percentage = serializers.IntegerField(source='level.company_percentage', read_only=True)
    level_individual_percentage = serializers.IntegerField(source='level.individual_percentage', read_only=True)

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
            'level_company_percentage',
            'level_individual_percentage',
            'manager',
            'manager_name',
        ]

# ========================
# OBJECTIVE SERIALIZER
# ========================
class ObjectiveSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # 🔥 FIX
    evaluation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Objective
        fields = '__all__'
# ========================
# EVALUATION SERIALIZER
# ========================
class EvaluationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        objectives = data.get('objectives', [])

        employee = data.get('employee') or getattr(self.instance, 'employee', None)

        if employee:
            total_weight = sum(obj.get('weight', 0) for obj in objectives)
            max_weight = employee.level.individual_percentage

            if total_weight > max_weight:
                raise serializers.ValidationError(
                    f"Total weight cannot exceed {max_weight}%"
                )

        return data

    employee_name = serializers.CharField(source='employee.name', read_only=True)

    # 🔥 Nested objectives (IMPORTANT)
    objectives = ObjectiveSerializer(many=True, required=False)

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

    def update(self, instance, validated_data):
        objectives_data = validated_data.pop('objectives', None)

        instance.employee_comment = validated_data.get(
            'employee_comment', instance.employee_comment
        )
        instance.manager_comment = validated_data.get(
            'manager_comment', instance.manager_comment
        )

        # only set when manager submits
        if 'manager_comment' in validated_data:
            instance.date_completed = timezone.now().date()

        instance.save()

        if objectives_data is not None:
            for index, obj_data in enumerate(objectives_data, start=1):
                obj_id = obj_data.get('id')

                if obj_id:
                    # 🔥 UPDATE EXISTING
                    try:
                        obj = instance.objectives.get(id=obj_id)
                    except Objective.DoesNotExist:
                        continue
                else:
                    # 🔥 CREATE NEW OBJECTIVE
                    obj = Objective(evaluation=instance)

                # 🔥 APPLY FIELDS (for BOTH cases)
                obj.order = index
                obj.description = obj_data.get('description', obj.description)
                obj.due_when = obj_data.get('due_when', obj.due_when)
                obj.weight = obj_data.get('weight', obj.weight)
                obj.measure = obj_data.get('measure', obj.measure)
                obj.target = obj_data.get('target', obj.target)

                obj.employee_actual = obj_data.get('employee_actual', obj.employee_actual)
                obj.manager_actual = obj_data.get('manager_actual', obj.manager_actual)

                obj.save()

        return instance

    # ========================
    # CREATE (with objectives)
    # ========================
    def create(self, validated_data):
        objectives_data = validated_data.pop('objectives')

        evaluation = Evaluation.objects.create(
            **validated_data,
            date_completed=timezone.now().date()
        )

        for index, obj_data in enumerate(objectives_data, start=1):
            Objective.objects.create(
                evaluation=evaluation,
                order=index,  # 🔥 FIX HERE
                **obj_data
            )

        return evaluation

        # ========================
        # 🔁 UPDATE EXISTING
        # ========================
        if existing:
            # update basic fields
            existing.employee_comment = validated_data.get(
                'employee_comment', existing.employee_comment
            )

            existing.date_completed = timezone.now().date()
            existing.save()

            # 🔥 replace objectives
            existing.objectives.all().delete()

            for obj_data in objectives_data:
                Objective.objects.create(evaluation=existing, **obj_data)

            return existing

        # ========================
        # 🆕 CREATE NEW
        # ========================
        evaluation = Evaluation.objects.create(
            **validated_data,
            date_completed=timezone.now().date()
        )

        for obj_data in objectives_data:
            Objective.objects.create(evaluation=evaluation, **obj_data)

        return evaluation