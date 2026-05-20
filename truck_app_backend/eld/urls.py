from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ELDLogView, ELDLogView

urlpatterns = [
    path("generate-logs/", ELDLogView.as_view()),
    path('generate-logs/<int:pk>/', ELDLogView.as_view()),
]