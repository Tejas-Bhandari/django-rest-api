from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    CustomUserSearchView,
    SendFriendRequestView,
    RespondToFriendRequestView,
    ListFriendsView,
    ListPendingFriendRequestsView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("search/", CustomUserSearchView.as_view(), name="user-search"),
    path(
        "send-friend-request/",
        SendFriendRequestView.as_view(),
        name="send-friend-request",
    ),
    path(
        "respond-to-friend-request/<int:friend_request_id>/",
        RespondToFriendRequestView.as_view(),
        name="respond-to-friend-request",
    ),
    path("list-friends/", ListFriendsView.as_view(), name="list-friends"),
    path(
        "list-pending-friend-requests/",
        ListPendingFriendRequestsView.as_view(),
        name="list-pending-friend-requests",
    ),
]
