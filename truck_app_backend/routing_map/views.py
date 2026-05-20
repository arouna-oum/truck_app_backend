from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.route_service import get_route
# Create your views here.


class RouteView(APIView):

    def post(self, request):

        origin = request.data["origin"]
        destination = request.data["destination"]

        route = get_route(origin, destination)

        return Response(route)