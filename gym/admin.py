from django.contrib import admin
from .models import Member, GymSession

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'subscription_start', 'subscription_end', 'has_active_subscription']
    search_fields = ['name', 'phone_number']
    list_filter = ['is_in_gym', 'subscription_start'] 
    readonly_fields = ['has_active_subscription']
    
    def has_active_subscription(self, obj):
        return obj.has_active_subscription
    has_active_subscription.boolean = True
    has_active_subscription.short_description = "Active Subscription"
    
@admin.register(GymSession)
class GymSessionAdmin(admin.ModelAdmin):
    list_display = ['member', 'entry_time', 'exit_time', 'duration']
    list_filter = ['entry_time', 'exit_time']
    search_fields = ['member__name', 'member__phone_number']
    readonly_fields = ['member']
