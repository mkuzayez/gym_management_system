from django.core.management.base import BaseCommand
from django.utils import timezone
from gym.models import Member

class Command(BaseCommand):
    help = 'Reset is_in_gym status for all members at midnight'

    def handle(self, *args, **options):
        # Get all members who are currently in the gym
        members_in_gym = Member.objects.filter(is_in_gym=True)
        count = members_in_gym.count()
        
        # For each member in the gym, create a session and set is_in_gym to False
        for member in members_in_gym:
            if member.entry_time:
                member.exit_gym()  # This will create a session and set is_in_gym to False
            else:
                # If no entry time is recorded, just set is_in_gym to False
                member.is_in_gym = False
                member.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully reset is_in_gym status for {count} members')
        )
