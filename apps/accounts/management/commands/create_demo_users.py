import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from apps.accounts.permissions import ROLE_ADMIN, ROLE_ENGINEER, ROLE_SUPERVISOR

class Command(BaseCommand):
    help = 'Create demonstration accounts for Administrator, Engineer, and Supervisor roles.'

    def handle(self, *args, **options):
        demo_accounts = [
            {
                'username': 'admin',
                'email': 'admin@manufacturing-ai.internal',
                'password': os.getenv('DEMO_ADMIN_PASSWORD', 'AdminPass123!'),
                'role': ROLE_ADMIN,
                'first_name': 'Chief',
                'last_name': 'Admin'
            },
            {
                'username': 'engineer',
                'email': 'engineer@manufacturing-ai.internal',
                'password': os.getenv('DEMO_ENGINEER_PASSWORD', 'EngineerPass123!'),
                'role': ROLE_ENGINEER,
                'first_name': 'Field',
                'last_name': 'Engineer'
            },
            {
                'username': 'supervisor',
                'email': 'supervisor@manufacturing-ai.internal',
                'password': os.getenv('DEMO_SUPERVISOR_PASSWORD', 'SupervisorPass123!'),
                'role': ROLE_SUPERVISOR,
                'first_name': 'Plant',
                'last_name': 'Supervisor'
            },
        ]

        self.stdout.write(self.style.NOTICE("Setting up demo user accounts..."))

        for acc in demo_accounts:
            user, created = User.objects.get_or_create(
                username=acc['username'],
                defaults={
                    'email': acc['email'],
                    'first_name': acc['first_name'],
                    'last_name': acc['last_name'],
                    'is_staff': (acc['role'] == ROLE_ADMIN),
                }
            )
            user.set_password(acc['password'])
            user.is_active = True
            if acc['role'] == ROLE_ADMIN:
                user.is_staff = True
            user.save()

            # Assign group
            group, _ = Group.objects.get_or_create(name=acc['role'])
            # Clear previous role groups to guarantee clean state
            for r in [ROLE_ADMIN, ROLE_ENGINEER, ROLE_SUPERVISOR]:
                g = Group.objects.filter(name=r).first()
                if g:
                    user.groups.remove(g)
            user.groups.add(group)

            action_str = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(
                f"[{action_str}] User '{acc['username']}' with Role: {acc['role']} (Password: {acc['password']})"
            ))

        self.stdout.write(self.style.SUCCESS("All demo accounts are ready."))
