from math import radians, sin, cos, atan2, sqrt, floor

from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from REST.models import MyUser, Friend, Message
from REST.serializers import PasswordChangeSerializer, RegistrationSerializer, PersonSerializer, ShowFriendSerializer, \
    UpdateFriendSerializer, MessageSerializer, UpdateMessagesSerializer, UserWithDistanceSerializer
from REST.utils import get_tokens_for_user

from testChatREST import settings


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.POST.get('email')
        print('Email:', email)
        password = request.POST.get('password')
        print('password:', password)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            return Response({'msg': 'Login Success', 'username': user.username, 'localId': user.id,
                             'profile_picture': user.profile_picture,
                             'access_token_lifetime': settings.ACCESS_TOKEN_LIFETIME,
                             'refresh_token_lifetime': settings.REFRESH_TOKEN_LIFETIME, **auth_data},
                            status=status.HTTP_200_OK)
        return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'msg': 'Successfully Logged out'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'msg': 'The password has been changed'}, status=status.HTTP_200_OK)


class PersonList(APIView):
    def get(self, request):
        person = MyUser.objects.all()
        serializer = PersonSerializer(person, many=True)
        return Response(serializer.data)


class PersonInfo(APIView):
    def get(self, request, person_id):
        try:
            person = MyUser.objects.get(pk=person_id)
        except MyUser.DoesNotExist:
            return Response(status=404)
        serializer = PersonSerializer(person)
        return Response(serializer.data)

    def patch(self, request, person_id, format=None):
        my_model = MyUser.objects.get(pk=person_id)
        serializer = PersonSerializer(my_model, data=request.data, partial=True)  # Uwaga na parametr `partial=True`
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendList(APIView):
    """
    List all friend, or add a new friend.
    """

    def delete(self, request, *args, **kwargs):
        try:
            person = request.data['person']
            friend = request.data['friend']
            friend_obj = Friend.objects.get(person=person, friend=friend)
            friend_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, person_id):
        try:
            person = MyUser.objects.get(pk=person_id)
            friend = Friend.objects.filter(person=person)
        except MyUser.DoesNotExist:
            return Response(status=404)

        serializer = ShowFriendSerializer(friend, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UpdateFriendSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageListCreateView(APIView):
    serializer_class = MessageSerializer

    def get(self, request):
        sender = request.query_params.get('sender')
        receiver = request.query_params.get('receiver')
        queryset = Message.objects.filter(sender=sender, receiver=receiver).order_by(
            'created_at') | Message.objects.filter(sender=receiver, receiver=sender).order_by('created_at')
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UpdateMessagesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def calculate_distance(request, user1_id, user2_id):
    user1 = get_object_or_404(MyUser, id=user1_id)
    user2 = get_object_or_404(MyUser, id=user2_id)

    # Konwersja na radiany
    lat1, lon1, lat2, lon2 = map(radians, [user1.latitude, user1.longitude, user2.latitude, user2.longitude])

    # Obliczenie odległości używając wzoru haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c * 1000  # Odległość w metrach

    return JsonResponse({'distance': distance})


def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Odległość w km
    distance = floor(distance)  # Zaokrąglij w dół
    return distance


@api_view(['GET'])
def list_users_with_distance(request, user_id):
    base_user = get_object_or_404(MyUser, id=user_id)
    all_users = MyUser.objects.exclude(id=user_id)

    serialized_users = []
    for user in all_users:
        distance = haversine_distance(base_user.latitude, base_user.longitude, user.latitude, user.longitude)
        user_data = UserWithDistanceSerializer(user).data
        user_data['distance'] = distance
        serialized_users.append(user_data)

    return Response(serialized_users)
