from django.contrib import admin
from .models import Member, GymSession

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'subscription_start', 'subscription_end', 'is_in_gym')
    search_fields = ('name', 'phone_number')
    list_filter = ('is_in_gym', 'is_active')

@admin.register(GymSession)
class GymSessionAdmin(admin.ModelAdmin):
    list_display = ('member', 'entry_time', 'exit_time', 'duration')
    search_fields = ('member__name', 'member__phone_number')
    list_filter = ('entry_time',)
