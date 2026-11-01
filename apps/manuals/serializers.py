from rest_framework import serializers
from .models import Manual
from .validators import validate_pdf_file

class ManualSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source='machine.name', read_only=True)
    machine_model = serializers.CharField(source='machine.model_number', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', default='System', read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)

    class Meta:
        model = Manual
        fields = [
            'id', 'machine', 'machine_name', 'machine_model', 'title',
            'file', 'original_filename', 'model_information', 'revision',
            'file_size', 'file_size_mb', 'page_count', 'chunk_count',
            'processing_status', 'error_message', 'uploaded_by',
            'uploaded_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'file_size_mb', 'page_count', 'chunk_count',
            'processing_status', 'error_message', 'uploaded_by', 'uploaded_by_username',
            'created_at', 'updated_at'
        ]

    def validate_file(self, value):
        validate_pdf_file(value)
        return value

class ManualUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manual
        fields = ['machine', 'title', 'file', 'model_information', 'revision']

    def validate_file(self, value):
        validate_pdf_file(value)
        return value

    def create(self, validated_data):
        file_obj = validated_data['file']
        manual = Manual.objects.create(
            machine=validated_data['machine'],
            title=validated_data['title'],
            file=file_obj,
            original_filename=file_obj.name,
            model_information=validated_data.get('model_information', ''),
            revision=validated_data.get('revision', 'Rev 1.0'),
            file_size=file_obj.size,
            uploaded_by=self.context['request'].user
        )
        return manual
