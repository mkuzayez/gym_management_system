from django.core.management.base import BaseCommand
from django.utils import timezone
from gym.models import Member

class Command(BaseCommand):
    """
    Management command to reset gym status for all members
    
    This command is intended to be run daily at midnight to ensure
    that any members who forgot to check out are properly logged out
    and their sessions are recorded.
    """
    help = 'Reset is_in_gym status for all members at midnight'

    def handle(self, *args, **options):
        # Get all members who are currently in the gym
        members_in_gym = Member.objects.filter(is_in_gym=True)
        count = members_in_gym.count()
        
        # For each member in the gym, create a session and set is_in_gym to False
        for member in members_in_gym:
            if member.entry_time:
                # This will create a session and set is_in_gym to False
                member.exit_gym()  
            else:
                # If no entry time is recorded, just set is_in_gym to False
                member.is_in_gym = False
                member.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully reset is_in_gym status for {count} members')
        )
