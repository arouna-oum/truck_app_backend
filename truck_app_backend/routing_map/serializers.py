from rest_framework import serializers

class RouteSerializer(serializers.Serializer):
    origin = serializers.ListField()
    destination = serializers.ListField()