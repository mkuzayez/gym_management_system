from rest_framework import serializers
from .models import Member, GymSession

class MemberSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Member
        fields = ('id', 'phone_number', 'name', 'password', 'subscription_start', 
                  'subscription_end', 'is_in_gym', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'is_in_gym')
    
    def create(self, validated_data):
        user = Member.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password'],
            subscription_start=validated_data.get('subscription_start'),
            subscription_end=validated_data.get('subscription_end')
        )
        return user

class MemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('name', 'subscription_start', 'subscription_end')

class GymSessionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    
    class Meta:
        model = GymSession
        fields = ('id', 'member', 'member_name', 'entry_time', 'exit_time', 'duration')
        read_only_fields = ('id', 'member_name', 'duration')
