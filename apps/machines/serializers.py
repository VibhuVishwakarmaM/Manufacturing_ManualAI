from rest_framework import serializers
from .models import Machine

class MachineSerializer(serializers.ModelSerializer):
    manual_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Machine
        fields = ['id', 'name', 'model_number', 'manufacturer', 'description', 'status', 'manual_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'manual_count']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Machine name cannot be blank.")
        return value.strip()

    def validate_model_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("Model number cannot be blank.")
        return value.strip()
