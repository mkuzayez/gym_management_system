from django.core.management.base import BaseCommand
from gym.models import Member

class Command(BaseCommand):
    """
    Management command to update subscription status for all members
    
    This command is intended to be run daily to ensure that the
    has_active_subscription property is up-to-date for all members.
    It's useful for keeping track of expired subscriptions.
    """
    help = 'Updates subscription status for all members'

    def handle(self, *args, **options):
        members = Member.objects.all()
        count = 0
        
        for member in members:
            # Save will trigger the logic to update has_active_subscription
            member.save()
            count += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated subscription status for {count} members')
        )
