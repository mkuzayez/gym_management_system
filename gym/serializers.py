from rest_framework import serializers
from .models import Member, GymSession
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Member
from rest_framework_simplejwt.tokens import RefreshToken


class MemberSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

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


class MemberRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
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
        password = validated_data.pop("password")
        # Create User for authentication
        user = User.objects.create_user(
            username=validated_data["phone_number"], password=password
        )
        # Create Member profile
        member = Member.objects.create(**validated_data)
        return member


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

        # Check if user exists and password is correct
        try:
            user = User.objects.get(username=phone_number)
            if not user.check_password(password):
                raise serializers.ValidationError("Incorrect password")
        except User.DoesNotExist:
            raise serializers.ValidationError("Authentication credentials not found")

        # Generate tokens
        refresh = RefreshToken.for_user(user)

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
