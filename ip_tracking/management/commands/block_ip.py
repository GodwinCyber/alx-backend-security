from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = "Add an IP to the blacklist"

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to blocked')

    def handle(self, *args, **options):
        ip = options['ip_address']
        blocked, created = BlockedIP.objects.get_or_create(ip_address=ip)
        if created:
            self.stdout.write(self.style.SUCCESS(f"IP {ip} successfully blocked."))
        else:
            self.stdout.write(self.style.WARNING(f"IP {ip} is already blocked."))



