"""
Management command to block IP addresses.

Task 1: Create a management command to add IPs to BlockedIP.
"""
from django.core.management.base import BaseCommand
from apps.security.models import BlockedIP


class Command(BaseCommand):
    help = 'Block an IP address by adding it to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address to block (IPv4 or IPv6)'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for blocking this IP'
        )

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        reason = options['reason'] or 'Manually blocked via management command'

        try:
            blocked_ip, created = BlockedIP.objects.get_or_create(
                ip_address=ip_address,
                defaults={'reason': reason}
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully blocked IP: {ip_address}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'IP {ip_address} is already blocked (blocked at: {blocked_ip.created_at})'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error blocking IP {ip_address}: {str(e)}'
                )
            )
