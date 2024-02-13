from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import CustomUser
from .models import FriendRequest
from django.contrib.auth import get_user_model
from .serializers import FriendRequestSerializer
from django.db.models import Q
from django_ratelimit.decorators import ratelimit

from .serializers import CustomUserSerializer


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class CustomUserSearchView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search_keyword = request.query_params.get("search", "")
        users = CustomUser.objects.filter(
            email__iexact=search_keyword
        ) | CustomUser.objects.filter(username__icontains=search_keyword)

        paginated_users = self.paginate_queryset(users, request)

        serializer = CustomUserSerializer(paginated_users, many=True)
        return self.get_paginated_response(serializer.data)


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get("to_user_id")
        to_user = get_user_model().objects.get(id=to_user_id)

        friend_request = FriendRequest(
            from_user=request.user, to_user=to_user, status="pending"
        )
        friend_request.save()

        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RespondToFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_request_id):
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if request.user == friend_request.to_user:
            action = request.data.get("action")

            if action == "accept":
                friend_request.status = "accepted"
            elif action == "reject":
                friend_request.status = "rejected"

            friend_request.save()

            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


class ListFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = FriendRequest.objects.filter(
            (
                Q(from_user=request.user, status="accepted")
                | Q(to_user=request.user, status="accepted")
            )
        )

        friend_users = []
        for friend_request in friends:
            friend_users.append(friend_request)

        serializer = FriendRequestSerializer(friend_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListPendingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = FriendRequest.objects.exclude(
            (
                Q(from_user=request.user, status="accepted")
                | Q(to_user=request.user, status="accepted")
            )
        )

        friend_users = []
        for friend_request in friends:
            friend_users.append(friend_request)

        serializer = FriendRequestSerializer(friend_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
