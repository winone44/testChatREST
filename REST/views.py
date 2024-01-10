from datetime import timedelta
from math import radians, sin, cos, atan2, sqrt, floor

from django.contrib.auth import login, authenticate, logout
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from REST.models import MyUser, Friend, Message, Group, Alert
from REST.serializers import PasswordChangeSerializer, RegistrationSerializer, PersonSerializer, ShowFriendSerializer, \
    UpdateFriendSerializer, MessageSerializer, UpdateMessagesSerializer, UserWithDistanceSerializer, GroupSerializer, \
    GroupDetailSerializer, AlertSerializer, AlertSerializerSave
from REST.utils import get_tokens_for_user

from testChatREST import settings

from django.utils.translation import gettext as _


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
            return Response({'error': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.POST.get('email')
        print('Email:', email)
        password = request.POST.get('password')
        print('password:', password)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            return Response({'message': _('Login Success'), 'username': user.username, 'localId': user.id,
                             'profile_picture': user.profile_picture,
                             'access_token_lifetime': settings.ACCESS_TOKEN_LIFETIME,
                             'refresh_token_lifetime': settings.REFRESH_TOKEN_LIFETIME, **auth_data},
                            status=status.HTTP_200_OK)
        return Response({'error': _('Invalid Credentials')}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': _('Successfully Logged out')}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': _('The password has been changed')}, status=status.HTTP_200_OK)


class DeleteCurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": _("The user was successfully deleted")}, status=status.HTTP_200_OK)


class PersonList(APIView):
    def get(self, request):
        person = MyUser.objects.all()
        serializer = PersonSerializer(person, many=True)
        return Response(serializer.data)


class PersonInfo(APIView):
    def get(self, request, person_id):
        try:
            person = MyUser.objects.get(pk=person_id)
            user_data = PersonSerializer(person).data
            if timezone.now() - person.last_activity > timedelta(minutes=1):
                user_data['online'] = False
            else:
                user_data['online'] = True

        except MyUser.DoesNotExist:
            return Response(status=404)

        return Response(user_data)

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
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request):
        sender = request.user.id
        receiver = request.query_params.get('receiver')
        queryset = Message.objects.filter(sender=sender, receiver=receiver).order_by(
            'created_at') | Message.objects.filter(sender=receiver, receiver=sender).order_by('created_at')
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['sender'] = request.user.id
        serializer = UpdateMessagesSerializer(data=data)
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
def list_users_with_distance(request):
    current_user = request.user
    base_user = get_object_or_404(MyUser, id=current_user.id)
    all_users = MyUser.objects.exclude(id=current_user.id)

    serialized_users = []
    for user in all_users:
        distance = haversine_distance(base_user.latitude, base_user.longitude, user.latitude, user.longitude)
        user_data = UserWithDistanceSerializer(user).data
        user_data['distance'] = distance

        if timezone.now() - user.last_activity > timedelta(minutes=1):
            user_data['online'] = False
        else:
            user_data['online'] = True

        serialized_users.append(user_data)

    sorted_users = sorted(serialized_users, key=lambda x: x['distance'])

    return Response(sorted_users)


@api_view(['GET'])
def list_users_by_recent_message(request):
    current_user = request.user
    base_user = get_object_or_404(MyUser, id=current_user.id)

    # Pobranie identyfikatorów użytkowników z ostatnich wysłanych/otrzymanych wiadomości
    user_ids = Message.objects.filter(
        Q(sender=current_user) | Q(receiver=current_user)
    ).order_by('-created_at').values('sender_id', 'receiver_id').distinct()

    # Wyodrębnienie unikalnych identyfikatorów użytkowników
    unique_user_ids = set()
    for entry in user_ids:
        unique_user_ids.add(entry['sender_id'])
        unique_user_ids.add(entry['receiver_id'])
    if current_user.id in unique_user_ids:
        unique_user_ids.remove(current_user.id)

    # Pobranie użytkowników
    users = MyUser.objects.filter(id__in=unique_user_ids)

    # Sortowanie użytkowników
    def get_latest_message_date(user):
        latest_sent_message = user.sent_messages.order_by('created_at').last()
        latest_received_message = user.received_messages.order_by('created_at').last()

        # Pobranie najnowszej daty z wysłanych i otrzymanych wiadomości
        dates = [msg.created_at for msg in [latest_sent_message, latest_received_message] if msg]
        return max(dates) if dates else None

    users = sorted(users, key=get_latest_message_date, reverse=True)

    serialized_users = []

    for user in users:
        distance = haversine_distance(base_user.latitude, base_user.longitude, user.latitude, user.longitude)
        user_data = UserWithDistanceSerializer(user).data
        user_data['distance'] = distance

        if timezone.now() - user.last_activity > timedelta(minutes=1):
            user_data['online'] = False
        else:
            user_data['online'] = True

        serialized_users.append(user_data)

    return Response(serialized_users)


class UsersInGroup(APIView):
    def get(self, request, group_id):
        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        users = group.users.all()
        serializer = PersonSerializer(users, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def check_user_activity(request, user_id):
    try:
        user = MyUser.objects.get(pk=user_id)
        if timezone.now() - user.last_activity > timedelta(minutes=1):
            return Response({'status': 'Nieaktywny'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Aktywny'}, status=status.HTTP_200_OK)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            request.user.groups.add(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        group_id = request.data.get('group_id')
        password = request.data.get('password')

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({'error': _('Group not found')}, status=status.HTTP_404_NOT_FOUND)

        if group.check_password(password):
            request.user.groups.add(group)
            return Response({'message': _('User added to group')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': _('Incorrect password')}, status=status.HTTP_400_BAD_REQUEST)


class LeaveGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        group_id = request.data.get('group_id')

        try:
            group = Group.objects.get(id=group_id)
            request.user.groups.remove(group)
            return Response({'message': _('User removed from group')}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': _('Group not found')}, status=status.HTTP_404_NOT_FOUND)


class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = GroupDetailSerializer(group)
        return Response(serializer.data)


class CustomPagination(PageNumberPagination):
    page_size = 2  # Ustawia liczbę elementów na stronie
    page_size_query_param = 'page_size'  # Umożliwia klientowi wybór liczby elementów na stronie
    max_page_size = 100  # Maksymalna dopuszczalna liczba elementów na stronie

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.page.previous_page_number() if self.page.has_previous() else None,
            'results': data
        })


class AlertListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        current_time = timezone.now()
        user_groups = request.user.groups.all()

        # Filtrowanie komunikatów na podstawie przynależności do grup oraz daty startu i końca
        alerts = Alert.objects.filter(
            group__in=user_groups,
            start_date__lte=current_time,
            end_date__gte=current_time
        ).order_by('end_date')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(alerts, request)

        if page is not None:
            serializer = AlertSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AlertSerializerSave(data=request.data)
        if serializer.is_valid():
            # Możesz dodać dodatkową logikę, np. sprawdzenie, czy użytkownik należy do grupy
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
