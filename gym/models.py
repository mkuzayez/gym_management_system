from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone


class MemberManager(BaseUserManager):
    """
    Custom manager for Member model that handles user creation
    """
    def create_user(self, phone_number, name, password=None, **extra_fields):
        """Create and save a regular member with the given details"""
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(phone_number=phone_number, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password=None, **extra_fields):
        """Create and save a superuser with the given details"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone_number, name, password, **extra_fields)


class Member(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for gym members with subscription tracking
    """
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    subscription_start = models.DateField(default=timezone.now) 
    subscription_end = models.DateField(null=True, blank=True)
    is_in_gym = models.BooleanField(default=False)
    entry_time = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = MemberManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    @property
    def has_active_subscription(self):
        """Check if member has an active subscription"""
        today = timezone.now().date()
        
        # Convert subscription_start to date if it's a datetime
        start_date = self.subscription_start
        if hasattr(start_date, 'date'):
            start_date = start_date.date()
        
        # Check if subscription_end exists and is in the future
        if self.subscription_end:
            end_date = self.subscription_end
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
            return start_date <= today <= end_date
        
        # If no end date is set, check if subscription has started
        return start_date <= today
    
    def enter_gym(self):
        """Record member entry to the gym"""
        if self.is_in_gym:
            return False, "Already in the gym"
            
        self.is_in_gym = True
        self.entry_time = timezone.now()
        self.save()
        return True, "Successfully entered the gym"

    def exit_gym(self):
        """Record member exit from the gym and create a session record"""
        if not self.is_in_gym:
            return False, "Not currently in the gym"
            
        if not self.entry_time:
            self.is_in_gym = False
            self.save()
            return True, "Gym status reset"
            
        exit_time = timezone.now()
        duration = exit_time - self.entry_time

        # Create a new gym session
        GymSession.objects.create(
            member=self,
            entry_time=self.entry_time,
            exit_time=exit_time,
            duration=duration.total_seconds() / 60,  # Duration in minutes
        )

        # Update member status
        self.is_in_gym = False
        self.entry_time = None
        self.save()
        return True, "Successfully exited the gym and session recorded"


class GymSession(models.Model):
    """
    Model to track member gym sessions including entry, exit and duration
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sessions')
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField()
    duration = models.FloatField(help_text="Duration in minutes")
    
    class Meta:
        ordering = ['-entry_time']  # Most recent sessions first
    
    def __str__(self):
        return f"{self.member.name} - {self.entry_time.strftime('%Y-%m-%d %H:%M')}"
