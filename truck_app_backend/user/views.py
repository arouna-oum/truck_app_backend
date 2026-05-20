from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import *
from rest_framework.views import APIView, csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
import requests
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, logout
from django.db import transaction

# Create your views here.
class UserListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        print('Hi--------------')
        serializer = UserSerializer(data=request.data)
        print('A Hi--------------')
        userModel = get_user_model()
        print('B Hi--------------')
        userName = request.data.get('username')
        email = request.data.get('email')
        if userModel.objects.filter(Q(username__iexact=userName) | Q(email__iexact=email)).exists():
            print('a user with this email or username exists already')
            return Response({'message':'A user with this email or username'}, status=status.HTTP_409_CONFLICT)

        if serializer.is_valid():
            print('Valid--------------')
            user = userModel.objects.create_user(
                username = serializer.validated_data['username'],
                first_name = serializer.validated_data['first_name'],
                last_name = serializer.validated_data['last_name'],
                password = serializer.validated_data['password'],
                email = serializer.validated_data['email'],
                phone = serializer.validated_data['phone']
            )
            print('Created--------------')
            user.save()
            print('Saved--------------')
            user_serializer = UserSerializer(user).data
            refresh = RefreshToken.for_user(user)
            user_serializer['access'] = str(refresh.access_token)
            user_serializer['refresh'] = str(refresh)
            return Response(user_serializer, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response({'message':'Not all the fields are filled'}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def patch(self, request, pk):
        userModel = get_user_model()
        try:
            user = userModel.objects.get(id=pk)
        except userModel.DoesNotExist:
            return Response({'message':'This user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        token = request.META.get('HTTP_AUTHORIZATION')
        print(f'the token sent is {token}')
        if token:
            token_bearer=token[7:] if token.lower().startswith('bearer ') else token
            print(f'the token sent is {token_bearer}')
            user_serializer = UserSerializer(data=request.data)
            fields = ['email','phone','username']
            if all(request.data.get(key) is not None for key in fields) and not request.data.get('profile_picture'):
                username = request.data.get('username')
                is_user = userModel.objects.filter(username__iexact=username)
                if not is_user.exists() or user.username==username:
                    user.username = username
                    user.email = request.data['email']
                    user.phone = request.data['phone']
                    user.first_name = request.data['first_name']
                    user.last_name = request.data['last_name']
                    user.save()
                    print('User have been modified success ', request.data['email'])
                    serializer = UserSerializer(user).data
                    print('User have been modified success 2=====  ', serializer)
                    serializer['access'] = token_bearer
                    serializer['refresh'] = request.data['refresh']
                    return Response(serializer, status=status.HTTP_200_OK)
                print('This user already exists')
                return Response({'message': 'This username already exists'}, status=status.HTTP_404_NOT_FOUND)
            elif request.data.get('profile_picture') is not None:
                username = request.data.get('username')
                is_user = userModel.objects.filter(username__iexact=username)
                if not is_user.exists() or user.username==username:
                    user.username = username
                    user.email = request.data['email']
                    user.profile_picture = request.data['profile_picture']
                    user.phone = request.data['phone']
                    user.first_name = request.data['first_name']
                    user.last_name = request.data['last_name']
                    user.save()
                    print('User have been modified success ', request.data['profile_picture'])
                    serializer = UserSerializer(user).data
                    print('User have been modified success 2=====  ', serializer)
                    serializer['access'] = token_bearer
                    serializer['refresh'] = request.data['refresh']
                    return Response(serializer, status=status.HTTP_200_OK)
                print('This user already exists')
                return Response({'message': 'This username already exists'}, status=status.HTTP_404_NOT_FOUND)
            print('Not all credentials are valid')
            return Response({'message': 'Not all fields are valid'}, status=status.HTTP_404_NOT_FOUND)
        print('No token is found, hence user is not authenticated')
        return Response({'message': 'login'}, status=status.HTTP_404_NOT_FOUND)

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(f"the name to be sent is {request.data['email']}")
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'message':'The credentials are not provided to proceed'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            return Response(
                {'message': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(username=user_obj.username, password=password)
        print(f'the user is {user}')
        if user is not None:
            print('User Authentified successfully')
            user_serializer = UserSerializer(user).data
            print(f'the user serializer is given as {user_serializer}')
            refresh = RefreshToken.for_user(user)
            print(f"The value of the request I've sent is equals to {refresh}")

            user_serializer['access'] = str(refresh.access_token)
            user_serializer['refresh'] = str(refresh)
            return Response(user_serializer, status=status.HTTP_200_OK)
        return Response({'message': 'Not all the fields are filled'}, status=status.HTTP_404_NOT_FOUND)

class UserLogOut(APIView):
    permission_classes = [IsAuthenticated]
    userModel = get_user_model()
    def post(self, request):
        refresh_token = request.data['refresh_token']
        # user = get_object_or_404(self.userModel,id=userId)
        user = request.user
        print(f"the value of refresh token is  {refresh_token}")
        if refresh_token is not None:
            token_object = RefreshToken(refresh_token)
            token_object.blacklist()
            user.status = False
            user.save()
            logout(request)
            return Response({'message':"User logout successfully"}, status=200)
        print('No refresh token sent here ')
        return Response({'message':'No refresh token sent '}, status=status.HTTP_404_NOT_FOUND)