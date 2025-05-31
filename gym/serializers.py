from rest_framework import serializers
from .models import Member, GymSession
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for Member model with complete fields
    Used for retrieving member details and registration
    """
    password = serializers.CharField(write_only=True, required=True)
    has_active_subscription = serializers.BooleanField(read_only=True)

    class Meta:
        model = Member
        fields = (
            "id",
            "phone_number",
            "name",
            "password",
            "subscription_start",
            "subscription_end",
            "is_in_gym",
            "date_joined",
            "has_active_subscription"
        )
        read_only_fields = ("id", "date_joined", "is_in_gym")

    def create(self, validated_data):
        """Create a new member with proper subscription dates"""
        # Ensure subscription_start is set to today if not provided
        if 'subscription_start' not in validated_data:
            validated_data['subscription_start'] = timezone.now().date()
            
        user = Member.objects.create_user(
            phone_number=validated_data["phone_number"],
            name=validated_data["name"],
            password=validated_data["password"],
            subscription_start=validated_data.get("subscription_start"),
            subscription_end=validated_data.get("subscription_end"),
        )
        return user


class MemberUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating member information
    Limited to only updatable fields
    """
    class Meta:
        model = Member
        fields = ("name", "subscription_start", "subscription_end")


class LoginSerializer(serializers.Serializer):
    """
    Serializer for member login with token generation
    """
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate credentials and generate tokens"""
        phone_number = data.get("phone_number")
        password = data.get("password")

        # Check if member exists
        try:
            member = Member.objects.get(phone_number=phone_number)
        except Member.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "No account found with this phone number"}
            )

        # Check if password is correct
        if not member.check_password(password):
            raise serializers.ValidationError(
                {"error": "Incorrect password"}
            )

        # Check subscription status
        if not member.has_active_subscription:
            raise serializers.ValidationError(
                {"error": "Your subscription has expired. Please renew to continue."}
            )

        # Generate tokens
        refresh = RefreshToken.for_user(member)

        return {
            "member": member,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class GymSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for gym session records
    """
    member_name = serializers.CharField(source="member.name", read_only=True)

    class Meta:
        model = GymSession
        fields = ("id", "member", "member_name", "entry_time", "exit_time", "duration")
        read_only_fields = ("id", "member_name", "duration")
