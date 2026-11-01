import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from apps.accounts.permissions import ROLE_ADMIN, ROLE_ENGINEER
from apps.machines.models import Machine
from apps.manuals.models import Manual

@pytest.fixture
def api_fixture(db):
    admin_grp, _ = Group.objects.get_or_create(name=ROLE_ADMIN)
    eng_grp, _ = Group.objects.get_or_create(name=ROLE_ENGINEER)

    admin = User.objects.create_user('admin_api', 'admin@api.com', 'AdminPass123!')
    admin.groups.add(admin_grp)

    engineer = User.objects.create_user('eng_api', 'eng@api.com', 'EngPass123!')
    engineer.groups.add(eng_grp)

    machine = Machine.objects.create(name='Drill Press DP-10', model_number='DP-10')

    return {
        'admin': admin,
        'engineer': engineer,
        'machine': machine
    }

@pytest.mark.django_db
class TestAPIEndpoints:

    def test_auth_login_and_me_endpoints(self, api_fixture):
        client = APIClient()

        # Login
        login_resp = client.post('/accounts/api/auth/login/', {
            'username': 'eng_api',
            'password': 'EngPass123!'
        })
        assert login_resp.status_code == 200
        assert 'user' in login_resp.data

        # Me endpoint
        me_resp = client.get('/accounts/api/auth/me/')
        assert me_resp.status_code == 200
        assert me_resp.data['username'] == 'eng_api'
        assert me_resp.data['role'] == ROLE_ENGINEER

    def test_dashboard_summary_endpoint(self, api_fixture):
        client = APIClient()
        client.force_authenticate(user=api_fixture['engineer'])

        resp = client.get('/dashboard/api/dashboard/summary/')
        assert resp.status_code == 200
        assert 'total_machines' in resp.data
        assert 'user_role' in resp.data

    def test_manual_status_endpoint(self, api_fixture):
        client = APIClient()
        client.force_authenticate(user=api_fixture['engineer'])

        manual = Manual.objects.create(
            machine=api_fixture['machine'],
            title='Drill Manual',
            original_filename='drill.pdf',
            processing_status='INDEXED',
            page_count=5,
            chunk_count=8
        )

        resp = client.get(f"/manuals/api/manuals/{manual.id}/status/")
        assert resp.status_code == 200
        assert resp.data['processing_status'] == 'INDEXED'
        assert resp.data['page_count'] == 5
        assert resp.data['chunk_count'] == 8

    def test_unauthorized_pdf_view_requires_authentication(self, api_fixture):
        client = APIClient()
        # Anonymous client attempting to view PDF
        resp = client.get(f"/manuals/11111111-1111-1111-1111-111111111111/view/")
        # Must redirect to login or return 401/403
        assert resp.status_code in [302, 401, 403]
