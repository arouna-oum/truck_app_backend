from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .services.log_generator import generate_eld_logs
from .models import ELDDailyLog
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from trip.models import Trip
from .services.log_generator import generate_eld_logs
# Create your views here.

class ELDLogView(APIView):

    def post(self, request):

        trip_id = request.data["trip_id"]
        distance = request.data["distance"]
        hours = request.data["hours"]

        result = generate_eld_logs(distance, hours)

        # OPTIONAL: save logs
        for day in result["daily_logs"]:

            ELDDailyLog.objects.create(
                trip_id=trip_id,
                day_number=day["day"],
                driving_hours=day["driving_hours"],
                on_duty_hours=day["on_duty_hours"],
                off_duty_hours=day["off_duty_hours"]
            )

        return Response(result)


class ELDLogView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):

        try:
            trip = Trip.objects.get(id=pk)

        except Trip.DoesNotExist:
            return Response(
                {"error": "Trip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # generate eld logs
        eld_logs = generate_eld_logs(
            distance_miles=trip.distance,
            total_hours=trip.duration
        )

        return Response({
            "trip_id": trip.id,
            "eld": eld_logs,
            "route_instructions": trip.route_instructions,
        }, status=status.HTTP_200_OK)