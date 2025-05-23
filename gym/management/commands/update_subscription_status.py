from django.core.management.base import BaseCommand
from gym.models import Member

class Command(BaseCommand):
    help = 'Updates has_active_subscription for all members'

    def handle(self, *args, **options):
        members = Member.objects.all()
        count = 0
        
        for member in members:
            # Save will trigger the logic to update has_active_subscription
            member.save()
            count += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {count} members')
        )