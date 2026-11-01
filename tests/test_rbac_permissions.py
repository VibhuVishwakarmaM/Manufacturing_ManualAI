import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from apps.accounts.permissions import ROLE_ADMIN, ROLE_ENGINEER, ROLE_SUPERVISOR
from apps.machines.models import Machine
from apps.manuals.models import Manual
from apps.question_history.models import QuestionHistory

@pytest.fixture
def rbac_setup(db):
    """Fixture initializing groups, test accounts, and basic machine."""
    admin_grp, _ = Group.objects.get_or_create(name=ROLE_ADMIN)
    eng_grp, _ = Group.objects.get_or_create(name=ROLE_ENGINEER)
    sup_grp, _ = Group.objects.get_or_create(name=ROLE_SUPERVISOR)

    admin_user = User.objects.create_user('test_admin', 'admin@test.com', 'AdminPass123!')
    admin_user.groups.add(admin_grp)

    engineer_user = User.objects.create_user('test_engineer', 'engineer@test.com', 'EngineerPass123!')
    engineer_user.groups.add(eng_grp)

    supervisor_user = User.objects.create_user('test_supervisor', 'sup@test.com', 'SupervisorPass123!')
    supervisor_user.groups.add(sup_grp)

    other_engineer = User.objects.create_user('test_engineer2', 'eng2@test.com', 'EngineerPass123!')
    other_engineer.groups.add(eng_grp)

    machine = Machine.objects.create(name='CNC Alpha', model_number='CNC-001')

    return {
        'admin': admin_user,
        'engineer': engineer_user,
        'supervisor': supervisor_user,
        'other_engineer': other_engineer,
        'machine': machine,
    }

@pytest.mark.django_db
class TestRBACPermissions:

    def test_anonymous_user_blocked_from_protected_endpoints(self, rbac_setup):
        client = APIClient()
        # API machine list
        resp = client.get('/machines/api/machines/')
        assert resp.status_code in [401, 403]

        # Web dashboard
        web_resp = client.get('/dashboard/')
        assert web_resp.status_code == 302
        assert '/accounts/login/' in web_resp.url

    def test_mandatory_test_1_engineer_cannot_upload_manual(self, rbac_setup):
        """
        MANDATORY ORGANIZER TEST 1:
        Verify that an Engineer cannot upload a manual or perform Administrator actions.
        """
        client = APIClient()
        client.force_authenticate(user=rbac_setup['engineer'])

        # 1. Engineer attempting API upload of manual must be rejected with 403 Forbidden
        upload_resp = client.post('/manuals/api/manuals/', {
            'machine': str(rbac_setup['machine'].id),
            'title': 'Unauthorized Manual Attempt',
        })
        assert upload_resp.status_code == 403, "Engineer must not be allowed to upload manuals via API"

        # 2. Engineer attempting web upload view must be redirected/denied
        web_upload_resp = client.get('/manuals/upload/')
        assert web_upload_resp.status_code == 302
        assert '/manuals/' in web_upload_resp.url or '/dashboard/' in web_upload_resp.url

        # 3. Engineer attempting machine registration must be rejected with 403
        machine_create_resp = client.post('/machines/api/machines/', {
            'name': 'Unauthorized Lathe',
            'model_number': 'LATHE-X'
        })
        assert machine_create_resp.status_code == 403, "Engineer must not be permitted to register machines"

        # 4. Engineer attempting user management must be rejected
        user_list_resp = client.get('/accounts/api/auth/users/')
        assert user_list_resp.status_code == 403, "Engineer must not be permitted to manage users"

    def test_administrator_can_perform_administrative_actions(self, rbac_setup):
        client = APIClient()
        client.force_authenticate(user=rbac_setup['admin'])

        # Admin can access user management API
        user_resp = client.get('/accounts/api/auth/users/')
        assert user_resp.status_code == 200

        # Admin can create machines
        machine_resp = client.post('/machines/api/machines/', {
            'name': 'Haas CNC Mill',
            'model_number': 'HAAS-VF3'
        })
        assert machine_resp.status_code == 201

    def test_supervisor_history_review_permissions(self, rbac_setup):
        """Supervisor can review cross-engineer query history."""
        # Create a query by engineer
        q1 = QuestionHistory.objects.create(
            user=rbac_setup['engineer'],
            machine=rbac_setup['machine'],
            question_text='How to lubricate axis?',
            answer_text='Apply SHC 007 grease.',
            status='ANSWERED'
        )

        client = APIClient()
        client.force_authenticate(user=rbac_setup['supervisor'])

        # Supervisor can review via API
        resp = client.get('/questions/api/supervisor/history/')
        assert resp.status_code == 200
        assert len(resp.data) >= 1

        # Engineer 2 attempting to access supervisor endpoint must be blocked
        client.force_authenticate(user=rbac_setup['other_engineer'])
        eng_resp = client.get('/questions/api/supervisor/history/')
        assert eng_resp.status_code == 403
