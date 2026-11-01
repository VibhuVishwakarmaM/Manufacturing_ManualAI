from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .permissions import ALL_ROLES, get_user_role

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'role', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login', 'role']

    def get_role(self, obj):
        return get_user_role(obj)

class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ALL_ROLES, default='Engineer')
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role']

    def create(self, validated_data):
        role_name = validated_data.pop('role', 'Engineer')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)
        return user

class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=ALL_ROLES)
    is_active = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        if 'role' in validated_data:
            new_role = validated_data['role']
            # Remove all existing role groups
            for r in ALL_ROLES:
                instance.groups.filter(name=r).delete()
            group, _ = Group.objects.get_or_create(name=new_role)
            instance.groups.add(group)
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if not username or not password:
            raise serializers.ValidationError('Must include username and password.')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials or account disabled.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs
