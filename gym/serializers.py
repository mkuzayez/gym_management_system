from rest_framework import serializers
from .models import Member, GymSession
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


class MemberSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    name = serializers.CharField(required=True)

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
    class Meta:
        model = Member
        fields = ("name", "subscription_start", "subscription_end")


class MemberLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get("phone_number")
        password = data.get("password")

        # Check if member exists
        try:
            member = Member.objects.get(phone_number=phone_number)
        except Member.DoesNotExist:
            raise serializers.ValidationError(
                "Member with this phone number does not exist"
            )

        # Check if password is correct
        if not member.check_password(password):
            raise serializers.ValidationError("Incorrect password")

        # Generate tokens
        refresh = RefreshToken.for_user(member)

        return {
            "member": member,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class GymSessionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)

    class Meta:
        model = GymSession
        fields = ("id", "member", "member_name", "entry_time", "exit_time", "duration")
        read_only_fields = ("id", "member_name", "duration")


class MemberRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = Member
        fields = (
            "phone_number",
            "name",
            "password",
            "subscription_start",
            "subscription_end",
        )

    def create(self, validated_data):
        # Ensure subscription_start is set to today if not provided
        if 'subscription_start' not in validated_data:
            validated_data['subscription_start'] = timezone.now().date()
            
        return Member.objects.create_user(
            phone_number=validated_data["phone_number"],
            name=validated_data["name"],
            password=validated_data["password"],
            subscription_start=validated_data.get("subscription_start"),
            subscription_end=validated_data.get("subscription_end"),
        )
