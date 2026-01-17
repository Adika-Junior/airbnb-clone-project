from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
import getpass

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--role',
            type=str,
            choices=['guest', 'host', 'admin'],
            help='Role for the superuser (guest/host/admin)'
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Use provided role without prompting'
        )

    def handle(self, *args, **options):
        role = options.get('role')
        noinput = options.get('noinput', False)
        
        # Get role interactively if not provided
        if not role and not noinput:
            self.stdout.write(self.style.WARNING('Please select a role for the superuser:'))
            self.stdout.write('  1. admin - Full access to all features')
            self.stdout.write('  2. host - Can manage properties and bookings')
            self.stdout.write('  3. guest - Standard user access')
            while True:
                role_input = input('Role (admin/host/guest) [admin]: ').strip().lower()
                if not role_input:
                    role = 'admin'
                    break
                elif role_input in ['admin', 'host', 'guest']:
                    role = role_input
                    break
                else:
                    self.stdout.write(self.style.ERROR('Invalid role. Please choose: admin, host, or guest'))
        
        # Default to admin if no role specified
        if not role:
            role = 'admin'
        
        # Remove role from options before calling super().handle
        options_without_role = {k: v for k, v in options.items() if k != 'role' and k != 'noinput'}
        
        # Call parent to create user
        super().handle(*args, **options_without_role)
        
        # After user is created, update the role
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get email from options or prompt
        email = options.get('email')
        if not email and not noinput:
            email = input('Email: ').strip()
        
        if email:
            try:
                user = User.objects.get(email=email)
                user.role = role
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created superuser "{user.email}" with role: {role}'
                ))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR("Superuser was not created or email not found."))
        else:
            # Try to get the last created superuser
            try:
                user = User.objects.filter(is_superuser=True).order_by('-date_joined').first()
                if user:
                    user.role = role
                    user.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Updated superuser "{user.email}" with role: {role}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating role: {e}"))
