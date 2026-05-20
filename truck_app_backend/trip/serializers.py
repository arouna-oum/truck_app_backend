from .models import Trip
from user.models import User
from user.serializers import UserSerializer
from rest_framework import serializers

class TripSerializer(serializers.ModelSerializer):
    assigned_driver = UserSerializer(read_only=True)

    assigned_driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_driver',
        write_only=True
    )

    co_driver = UserSerializer(read_only=True)

    co_driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='co_driver',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Trip
        exclude = ['created_at', 'updated_at']