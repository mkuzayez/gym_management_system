from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Member, GymSession
from .serializers import (
    MemberSerializer, 
    MemberUpdateSerializer, 
    GymSessionSerializer,
    LoginSerializer
)
from .permissions import HasActiveSubscription


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for member registration
    Returns user data and authentication tokens
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "phone_number": user.phone_number,
                    "subscription_start": user.subscription_start,
                    "subscription_end": user.subscription_end,
                    "has_active_subscription": user.has_active_subscription,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    API endpoint for member login
    Returns user data and authentication tokens
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            # The serializer's validate method already formats errors properly
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        validated_data = serializer.validated_data
        member = validated_data["member"]

        return Response(
            {
                "user": {
                    "id": member.id,
                    "name": member.name,
                    "phone_number": member.phone_number,
                    "subscription_start": member.subscription_start,
                    "subscription_end": member.subscription_end,
                    "has_active_subscription": member.has_active_subscription,
                },
                "refresh": validated_data["refresh"],
                "access": validated_data["access"],
            },
            status=status.HTTP_200_OK,
        )


class MemberListView(generics.ListAPIView):
    """
    API endpoint to list all members
    Only accessible by admin users
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAdminUser]


class MemberDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update member details
    GET: Accessible by the member themselves or admin
    PUT/PATCH: Only accessible by admin
    """
    queryset = Member.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return MemberSerializer
        return MemberUpdateSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), HasActiveSubscription()]


class MemberEnterGymView(APIView):
    """
    API endpoint for recording member entry to the gym
    """
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def post(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response(
                {"error": "Member not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is trying to update their own record or is admin
        if request.user.pk != pk and not request.user.is_staff:
            return Response(
                {"error": "You can only update your own gym status"},
                status=status.HTTP_403_FORBIDDEN
            )

        success, message = member.enter_gym()
        
        if not success:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({"success": message})


class MemberExitGymView(APIView):
    """
    API endpoint for recording member exit from the gym
    """
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def post(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response(
                {"error": "Member not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is trying to update their own record or is admin
        if request.user.pk != pk and not request.user.is_staff:
            return Response(
                {"error": "You can only update your own gym status"},
                status=status.HTTP_403_FORBIDDEN
            )

        success, message = member.exit_gym()
        
        if not success:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({"success": message})


class GymSessionListView(generics.ListAPIView):
    """
    API endpoint to list gym sessions
    Admin: Can view all sessions
    Members: Can only view their own sessions
    """
    serializer_class = GymSessionSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return GymSession.objects.all()
        return GymSession.objects.filter(member=user)
