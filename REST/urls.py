from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from REST.views import LoginView, LogoutView, ChangePasswordView, RegistrationView, FriendList, PersonList, PersonInfo, \
    MessageListCreateView, calculate_distance, list_users_with_distance, UsersInGroup, check_user_activity, \
    GroupCreateView, JoinGroupView, LeaveGroupView, GroupDetailView, list_users_by_recent_message, \
    DeleteCurrentUserView, AlertListCreateView

urlpatterns = [
    path('accounts/register', RegistrationView.as_view(), name='register'),
    path('accounts/login', LoginView.as_view(), name='register'),
    path('accounts/logout', LogoutView.as_view(), name='register'),
    path('accounts/change-password', ChangePasswordView.as_view(), name='register'),
    path('accounts/token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/friend/', FriendList.as_view(), name='friend'),
    path('accounts/friend/<int:person_id>/', FriendList.as_view(), name='friend-list'),
    path('accounts/person/', PersonList.as_view(), name='person-list'),
    path('accounts/person/<int:person_id>/', PersonInfo.as_view(), name='person-info'),
    path('accounts/person/<int:person_id>/patch/', PersonInfo.as_view(), name='person-update'),
    path('accounts/delete-account/', DeleteCurrentUserView.as_view(), name='delete-account'),
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('distance/<int:user1_id>/<int:user2_id>/', calculate_distance, name='calculate_distance'),
    path('list_users_with_distance/', list_users_with_distance, name='list_users_with_distance'),
    path('list_users_by_recent_message/', list_users_by_recent_message, name='list_users_by_recent_message'),
    path('check_user_activity/<int:user_id>/', check_user_activity, name='check_user_activity'),
    path('groups/<int:group_id>/users/', UsersInGroup.as_view(), name='users-in-group'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('group/create/', GroupCreateView.as_view(), name='group-create-view'),
    path('group/join/', JoinGroupView.as_view(), name='join-group-view'),
    path('group/leave/', LeaveGroupView.as_view(), name='leave-group-view'),
    path('groups/alerts/', AlertListCreateView.as_view(), name='alert-list-create-view'),
]
