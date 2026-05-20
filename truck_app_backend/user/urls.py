from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', views.UserLogOut.as_view(), name='logout'),
    path('login/', views.RegisterUserView.as_view(), name='login'),
    path('account/<int:pk>/', views.UserView.as_view(), name='account'),
    path('account/', views.UserView.as_view(), name='account'),
    path('all_users/', views.UserListView.as_view(), name='user_list'),
]