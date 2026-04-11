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
    id = serializers.IntegerField()
    evaluation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Objective
        fields = '__all__'

    class Meta:
        model = Objective
        fields = '__all__'

# ========================
# EVALUATION SERIALIZER
# ========================
class EvaluationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        objectives = data.get('objectives', [])

        # 🔥 FIX: handle PATCH (no employee in data)
        employee = data.get('employee') or self.instance.employee

        total_weight = sum(obj.get('weight', 0) for obj in objectives)
        max_weight = employee.level.individual_percentage

        if total_weight > max_weight:
            raise serializers.ValidationError(
                f"Total weight cannot exceed {max_weight}%"
            )

        return data

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

    def update(self, instance, validated_data):
        objectives_data = validated_data.pop('objectives', [])

        print("OBJECTIVES DATA:", objectives_data)  # ✅ here

        instance.manager_comment = validated_data.get(
            'manager_comment', instance.manager_comment
        )
        instance.save()

        for obj_data in objectives_data:
            print("SINGLE OBJECT:", obj_data)  # ✅ here

            obj_id = obj_data.get('id')

            try:
                obj = instance.objectives.get(id=obj_id)
            except Objective.DoesNotExist:
                print("OBJECT NOT FOUND:", obj_id)  # ✅ debug
                continue

            obj.manager_actual = obj_data.get('manager_actual', obj.manager_actual)
            obj.save()

        return instance

    # ========================
    # CREATE (with objectives)
    # ========================
    def create(self, validated_data):
        objectives_data = validated_data.pop('objectives')
        evaluation = Evaluation.objects.create(**validated_data)

        for obj_data in objectives_data:
            Objective.objects.create(evaluation=evaluation, **obj_data)

        return evaluation

