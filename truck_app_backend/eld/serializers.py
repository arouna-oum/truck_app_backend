from rest_framework import serializers
from eld.models import ELDDailyLog


class ELDDailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELDDailyLog
        fields = '__all__'