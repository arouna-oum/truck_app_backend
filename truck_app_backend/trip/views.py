from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *
from user.models import User
from django.db.models import Sum
from user.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
import requests
from django.db.models import Q
from rest_framework import status, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from geopy.geocoders import Nominatim, OpenCage
from geopy.extra.rate_limiter import RateLimiter
from django.conf import settings
from geopy.distance import geodesic
from routing_map.services.route_service import get_route
from eld.services.log_generator import generate_eld_logs
# Create your views here.

def status_choices(request):
    if request.method == 'GET':
        types = [{'value': key, 'label': label} for key, label in Trip.STATUS_CHOICES]
        print(f'the value of types is {types}')
        return JsonResponse({'status_choices': types})
    else:
        return JsonResponse({'error': 'GET method required'}, status=405)
    
def hos_choices(request):
    if request.method == 'GET':
        types = [{'value': key, 'label': label} for key, label in Trip.HOS_CHOICES]
        print(f'the value of types is {types}')
        return JsonResponse({'hos_choices': types})
    else:
        return JsonResponse({'error': 'GET method required'}, status=405)
    
def cargo_type_choices(request):
    if request.method == 'GET':
        types = [{'value': key, 'label': label} for key, label in Trip.CARGO_TYPE_CHOICES]
        print(f'the value of types is {types}')
        return JsonResponse({'cargo_type_choices': types})
    else:
        return JsonResponse({'error': 'GET method required'}, status=405)

class TripPagination(pagination.PageNumberPagination):
    page_size = 10

class TripView(viewsets.ModelViewSet):

    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['assigned_driver','origin','destination','departure_date','status','tractor_number','driver_number','hos_cycle']
    search_fields = ['assigned_driver']
    pagination_class = TripPagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # def retrieve(self, request, pk):
    #     userModel = get_user_model()
    #     driver = get_object_or_404(userModel, id=pk)
    #     print('print the driver exists ', driver)
    #     all_trips = Trip.objects.filter(assigned_driver=pk)
    #     filtering = self.filter_queryset(all_trips)
    #     page = self.paginate_queryset(filtering)

    #     if page is not None:
    #         serialized_data = self.serializer_class(page, many=True).data
    #         return self.get_paginated_response(serialized_data)
    #     else:
    #         print('there is an error that occured here now ')
    #         serializer = self.get_serializer(filtering, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK) 
    
    def retrieve(self, request, pk):
        userModel = get_user_model()
        driver = get_object_or_404(userModel, id=pk)

        all_trips = Trip.objects.filter(assigned_driver=pk)
        filtering = self.filter_queryset(all_trips)

        page = self.paginate_queryset(filtering)

        trips = page if page is not None else filtering

        enriched_trips = []

        for trip in trips:
            eld_logs = None

            if trip.distance and trip.route_geometry:
                duration_hours = trip.duration_hours if hasattr(trip, "duration_hours") else 0
                eld_logs = generate_eld_logs(trip.distance, duration_hours)

            trip_data = self.get_serializer(trip).data
            trip_data["eld"] = eld_logs

            enriched_trips.append(trip_data)

        if page is not None:
            return self.get_paginated_response(enriched_trips)

        return Response(enriched_trips)

    @transaction.atomic
    def create(self, request):
        print('Entered for creation')
        user_id = request.data.get('assigned_driver_id')
        user_b = request.data.get('co_driver_id')
        userModel = get_user_model()
        try:
            user = userModel.objects.get(id=user_id)
            if user_b is None:
                pass
            else:
                user_co_driver = get_object_or_404(userModel, id=user_b)
        except userModel.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TripSerializer(data=request.data)
        print(f"All the values for trip are correct {serializer}")
        if serializer.is_valid():
            print(f"All the values for trip are correct {serializer}")
            address_point_a = serializer.validated_data['origin']
            address_point_b = serializer.validated_data['destination']
            geolocator = OpenCage(api_key=settings.OPENCAGE_API_KEY,timeout=10)
            geocode = RateLimiter(
                geolocator.geocode,
                min_delay_seconds=1,  # required by Nominatim usage policy
                max_retries=3,        # ⬅️ retry on failure
                error_wait_seconds=5,
                swallow_exceptions=False
            )
            try:
                location_a = geocode(address_point_a)
                location_b = geocode(address_point_b)
                print("The location is shown to be:", location_a)

                # if location_a:
                    # print('the rawMap is shown to be equals to ', location_a)
                    
                # if location_b:
                    # print('the rawMap is shown to be equals to ', location_b)
                    
                route = get_route(
                    origin=(location_a.latitude, location_a.longitude),
                    destination=(location_b.latitude, location_b.longitude)
                )

                distance_miles = route["distance_miles"]
                duration_hours = route["duration_hours"]
                print("duration_hours=====================================:", duration_hours)
                eld_logs = generate_eld_logs(distance_miles, duration_hours)
                print("ELD LOGS=====================================:", eld_logs)
            except Exception as e:
                print("Geocoding failed:", e)
                return Response({'message': 'Geocoding failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            trip = Trip.objects.create(
                assigned_driver = user,
                co_driver = user_co_driver if user_b is not None else None,
                driver_number = serializer.validated_data['driver_number'],
                tractor_number = serializer.validated_data['tractor_number'],
                origin = serializer.validated_data['origin'],
                destination = serializer.validated_data['destination'],
                departure_date = serializer.validated_data['departure_date'],
                departure_time = serializer.validated_data['departure_time'],
                cargo_type = serializer.validated_data['cargo_type'],
                shipper_name = serializer.validated_data['shipper_name'],
                load_number = serializer.validated_data['load_number'],
                hos_cycle = serializer.validated_data['hos_cycle'],
                # current_cycle_used = serializer.validated_data['current_cycle_used'],
                duration = duration_hours,
                distance = distance_miles,
                route_geometry = route["geometry"],
                route_instructions = route["steps"],
                # status = serializer.validated_data['status']
            )
            print('Created--------------')
            trip.save()
            # print('The trip is shown to be:', trip)
            trip_serialize = TripSerializer(trip).data
            # print('The trip serializer shown is equals to ', trip_serialize)
            return Response({
                "trip": trip_serialize,
                "route": route,
                "eld": eld_logs}, status=status.HTTP_200_OK)
        
        print('The trip serializer is not valid ', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def partial_update(self, request, pk):
        print('Entered for update')
        user_id = request.data.get('assigned_driver')
        user_b = request.data.get('co_driver')
        userModel = get_user_model()
        try:
            user = userModel.objects.get(id=user_id)
            if user_b is None:
                pass
            else:
                user_co_driver = get_object_or_404(userModel, id=user_b)
        except userModel.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        trip = get_object_or_404(Trip, id=pk)
        print('The trip to update is shown to be:', trip)
        trip_serializer = TripSerializer(trip, data=request.data, partial=True)
        if trip_serializer.is_valid():
            address_point_a = trip_serializer.validated_data.get('origin')
            address_point_b = trip_serializer.validated_data.get('destination')
            geolocator = OpenCage(api_key=settings.OPENCAGE_API_KEY,timeout=10)
            geocode = RateLimiter(
                geolocator.geocode,
                min_delay_seconds=1,  # required by Nominatim usage policy
                max_retries=3,        # ⬅️ retry on failure
                error_wait_seconds=5,
                swallow_exceptions=False
            )
            location_a = geocode(address_point_a)
            location_b = geocode(address_point_b)
            if not location_a or not location_b:
                return Response({'message': 'Geocoding failed'}, status=status.HTTP_400_BAD_REQUEST)
            route = get_route(
                origin=(location_a.latitude, location_a.longitude),
                destination=(location_b.latitude, location_b.longitude)
            )

            distance_miles = route["distance_miles"]
            duration_hours = route["duration_hours"]
            eld_logs = generate_eld_logs(distance_miles, duration_hours)
            trip_serializer.validated_data['duration'] = duration_hours
            trip_serializer.validated_data['distance'] = distance_miles
            trip_serializer.validated_data['route_geometry'] = route["geometry"]

            trip_serializer.save(
                assigned_driver = user,
                co_driver = user_co_driver if user_b is not None else None
            )
            return Response({
    "trip": trip_serializer.data,
    "route": route,
    "eld": eld_logs
}, status=status.HTTP_200_OK)
        return Response(trip_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def destroy(self, request, pk):
        print('Entered to delete a trip')
        userModel = get_user_model()
        trip = get_object_or_404(Trip, id=pk)
        owner_id = request.query_params.get('owner')
        owner = get_object_or_404(userModel, id=owner_id)
        print(f"The driver issued is linked to this is {owner}")
        trip.delete()
        return Response({'message': 'Trip deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class LoadAllTrips(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # generate eld logs
        user_trips = user.assigned_trips.all()
        trips_serializer = TripSerializer(user_trips, many=True).data

        return Response(trips_serializer, status=status.HTTP_200_OK)

def getTrip_details(request, pk):
    if request.method == 'GET':
        userModel = get_user_model()
        user = get_object_or_404(userModel,id=pk)
        print('The user exists', user)
        total_trips = Trip.objects.filter(assigned_driver=pk).count()
        total_distance = Trip.objects.aggregate(distance = Sum('distance'))['distance']
        print('The total distance exists', total_distance)
        all_pending_trips = Trip.objects.filter(status='pending',assigned_driver=pk)
        all_in_transit_leases = Trip.objects.filter(status='in_transit',assigned_driver=pk)
        all_completed_leases = Trip.objects.filter(status='completed',assigned_driver=pk)
        all_cancelled_leases = Trip.objects.filter(status='cancelled',assigned_driver=pk)
        if all_pending_trips.exists() or all_in_transit_leases.exists() or all_completed_leases.count() or all_cancelled_leases.count():
            print(f'the total active leases are shown as {all_pending_trips.count()}')
            return JsonResponse({'distance': total_distance,'total':total_trips,'pending': all_pending_trips.count(),'in_transit': all_in_transit_leases.count(), 'cancelled': all_cancelled_leases.count(), 'completed': all_completed_leases.count()}, status=status.HTTP_200_OK)
        print('the all active leases is empty or None')
        return JsonResponse({'distance': 0,'total':total_trips,'pending': 0, 'in_transit':0, 'cancelled': 0, 'completed': 0}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Only GET method allowed'}, status=405)
    