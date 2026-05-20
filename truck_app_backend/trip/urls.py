from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'trip_actions', views.TripView, basename='trip_actions')

urlpatterns = [
    path('', include(router.urls)),
    path('all_trips/<int:pk>/', views.LoadAllTrips.as_view(), name='all_trips'),
    path('status_choices/', views.status_choices, name='status_choices'),
    path('hos_choices/', views.hos_choices, name='hos_choices'),
    path('cargo_type_choices/', views.cargo_type_choices, name='cargo_type_choices'),
]