from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.permissions import ROLE_ADMIN, ROLE_ENGINEER, ROLE_SUPERVISOR

class Command(BaseCommand):
    help = 'Automatically create Django Groups (Administrator, Engineer, Supervisor) and assign granular permissions.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing Django Groups and RBAC Permissions..."))

        # 1. Create or get Groups
        admin_group, created_admin = Group.objects.get_or_create(name=ROLE_ADMIN)
        engineer_group, created_eng = Group.objects.get_or_create(name=ROLE_ENGINEER)
        supervisor_group, created_sup = Group.objects.get_or_create(name=ROLE_SUPERVISOR)

        # Collect permissions
        # Administrator receives all permissions across app models
        all_perms = Permission.objects.filter(
            content_type__app_label__in=[
                'machines', 'manuals', 'document_processing', 
                'question_history', 'audit_logs', 'notifications'
            ]
        )
        admin_group.permissions.set(all_perms)

        # Engineer permissions:
        # Can view machines, view manuals, create question history, create feedback, view personal questions
        engineer_perms = Permission.objects.filter(
            content_type__app_label__in=['machines', 'manuals', 'question_history'],
            codename__in=[
                'view_machine', 'view_manual',
                'add_questionhistory', 'view_questionhistory',
                'add_answerfeedback', 'view_answerfeedback'
            ]
        )
        engineer_group.permissions.set(engineer_perms)

        # Supervisor permissions:
        # Can view machines, manuals, all question histories, feedbacks, and audit logs (read-only)
        supervisor_perms = Permission.objects.filter(
            content_type__app_label__in=['machines', 'manuals', 'question_history', 'audit_logs'],
            codename__in=[
                'view_machine', 'view_manual',
                'view_questionhistory', 'view_answerfeedback',
                'view_auditlog'
            ]
        )
        supervisor_group.permissions.set(supervisor_perms)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully configured roles:\n"
            f" - {ROLE_ADMIN}: {admin_group.permissions.count()} permissions\n"
            f" - {ROLE_ENGINEER}: {engineer_group.permissions.count()} permissions\n"
            f" - {ROLE_SUPERVISOR}: {supervisor_group.permissions.count()} permissions"
        ))
