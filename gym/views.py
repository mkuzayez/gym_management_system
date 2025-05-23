from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Member, GymSession
from .serializers import MemberSerializer, MemberUpdateSerializer, GymSessionSerializer
from rest_framework.permissions import AllowAny
from .serializers import MemberRegistrationSerializer, MemberLoginSerializer
from .permissions import HasActiveSubscription


class RegisterView(generics.CreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": MemberSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            return Response(
                {"error": "Please provide both phone number and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = Member.objects.get(phone_number=phone_number)
        except Member.DoesNotExist:
            return Response(
                {"error": "No user found with this phone number"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if the member has an active subscription
        if not user.has_active_subscription:
            return Response(
                {
                    "error": "Your subscription has expired. Please renew your subscription to continue."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "phone_number": user.phone_number,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class MemberListView(generics.ListAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAdminUser]  # Admin only, no change needed


class MemberDetailView(generics.RetrieveUpdateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberUpdateSerializer
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return MemberSerializer
        return MemberUpdateSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), HasActiveSubscription()]


class MemberEnterGymView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def post(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response(
                {"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is trying to update their own record or is admin
        if request.user.pk != pk and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if member.is_in_gym:
            return Response(
                {"error": "Member is already in the gym"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.enter_gym()
        return Response({"success": "Member has entered the gym"})


class MemberExitGymView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def post(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response(
                {"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is trying to update their own record or is admin
        if request.user.pk != pk and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not member.is_in_gym:
            return Response(
                {"error": "Member is not in the gym"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.exit_gym()
        return Response(
            {"success": "Member has exited the gym and session has been recorded"}
        )


class GymSessionListView(generics.ListAPIView):
    serializer_class = GymSessionSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return GymSession.objects.all().order_by("-entry_time")
        return GymSession.objects.filter(member=user).order_by("-entry_time")


class MemberRegistrationView(APIView):
    permission_classes = [AllowAny]  # No change needed for registration

    def post(self, request):
        serializer = MemberRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            return Response(
                {
                    "message": "Member registered successfully",
                    "member_id": member.id,
                    "name": member.name,
                    "phone_number": member.phone_number,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MemberLoginSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            member = validated_data["member"]

            # Check if the member has an active subscription
            if not member.has_active_subscription:
                return Response(
                    {
                        "error": "Your subscription has expired. Please renew your subscription to continue."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {
                    "user": {
                        "id": member.id,
                        "name": member.name,
                        "phone_number": member.phone_number,
                    },
                    "refresh": validated_data["refresh"],
                    "access": validated_data["access"],
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
