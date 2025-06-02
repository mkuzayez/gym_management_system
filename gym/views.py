from django.db import models
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Member, GymSession
from .serializers import MemberSerializer, MemberUpdateSerializer, LoginSerializer, GymSessionSerializer
from .permissions import HasActiveSubscription
from datetime import timedelta

class RegisterView(APIView):
    """
    API endpoint for member registration
    """
    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    """
    API endpoint for member login
    Returns user details and JWT tokens
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
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
    
    def list(self, request, *args, **kwargs):
        # Check and close long sessions before processing
        closed_count = check_and_close_long_sessions()
        if closed_count > 0:
            print(f"Auto-closed {closed_count} sessions that exceeded 1.5 hours")
            
        return super().list(request, *args, **kwargs)
        
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
        
    def retrieve(self, request, *args, **kwargs):
        # Check and close long sessions before processing
        check_and_close_long_sessions()
        return super().retrieve(request, *args, **kwargs)
        
class MemberEnterGymView(APIView):
    """
    API endpoint for recording member entry to the gym
    """
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]
    def post(self, request, pk):
        # Check and close long sessions before processing
        check_and_close_long_sessions()
        
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
        # Check and close long sessions before processing
        check_and_close_long_sessions()
        
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
        # Check and close long sessions before processing
        check_and_close_long_sessions()
        
        user = self.request.user
        if user.is_staff:
            return GymSession.objects.all()
        return GymSession.objects.filter(member=user)
class InGymMembersView(generics.ListAPIView):
    """
    API endpoint to list all members currently in the gym
    Accessible by any authenticated member with active subscription
    """
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]
    
    def get_queryset(self):
        # Check and close long sessions before processing
        check_and_close_long_sessions()
        
        """Return only members who are currently in the gym"""
        return Member.objects.filter(is_in_gym=True)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add count of members in gym to response
        return Response({
            "count": queryset.count(),
            "members": serializer.data
        })

class MemberRecentSessionsView(generics.ListAPIView):
    """
    API endpoint to retrieve recent sessions for a specific member by ID
    Limited to 50 most recent sessions
    Admin: Can view any member's sessions
    Members: Can only view their own sessions
    """
    serializer_class = GymSessionSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]
    
    def get_queryset(self):
        # Check and close long sessions before processing
        check_and_close_long_sessions()
        
        member_id = self.kwargs.get('id')
        
        # Check if member exists
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            return GymSession.objects.none()
        
        # Check permissions - only allow staff or the member themselves
        user = self.request.user
        if not user.is_staff and user.pk != member.pk:
            return GymSession.objects.none()
            
        # Return up to 50 most recent sessions for the member
        return GymSession.objects.filter(member=member).order_by('-entry_time')[:50]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # If queryset is empty due to permissions or non-existent member
        if not queryset.exists() and 'id' in self.kwargs:
            try:
                Member.objects.get(pk=self.kwargs.get('id'))
                # Member exists but user doesn't have permission
                if request.user.pk != self.kwargs.get('id') and not request.user.is_staff:
                    return Response(
                        {"error": "You can only view your own sessions"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Member.DoesNotExist:
                # Member doesn't exist
                return Response(
                    {"error": "Member not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "sessions": serializer.data
        })

def check_and_close_long_sessions():
    """
    Utility function to close sessions that have been open for more than 1.5 hours
    This is called when accessing session-related endpoints
    """
    # Calculate the cutoff time (1 hour and 30 minutes ago)
    cutoff_time = timezone.now() - timedelta(hours=1, minutes=30)
    
    # Find members who are in the gym with entry time older than the cutoff
    long_sessions = Member.objects.filter(
        is_in_gym=True,
        entry_time__lt=cutoff_time
    )
    
    # Close each session
    for member in long_sessions:
        member.exit_gym()
    
    return len(long_sessions)
