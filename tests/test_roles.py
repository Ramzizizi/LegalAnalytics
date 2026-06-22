from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.accounts.roles import is_analyst, is_editor, get_role_label, ROLE_EDITOR, ROLE_ANALYST, ROLE_READER

User = get_user_model()


def _make_user(username, group_name=None, is_staff=False):
    u = User.objects.create_user(username=username, password='p', is_staff=is_staff)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        u.groups.add(group)
    return u


class TestRoleHelpers(TestCase):
    def test_reader_is_not_analyst(self):
        u = _make_user('reader', ROLE_READER)
        assert not is_analyst(u)
        assert not is_editor(u)

    def test_analyst_is_analyst(self):
        u = _make_user('analyst', ROLE_ANALYST)
        assert is_analyst(u)
        assert not is_editor(u)

    def test_editor_is_analyst_and_editor(self):
        u = _make_user('editor', ROLE_EDITOR)
        assert is_analyst(u)
        assert is_editor(u)

    def test_staff_is_analyst_and_editor(self):
        u = _make_user('admin', is_staff=True)
        assert is_analyst(u)
        assert is_editor(u)

    def test_no_group_user_is_not_analyst(self):
        u = _make_user('nogroup')
        assert not is_analyst(u)
        assert not is_editor(u)

    def test_get_role_label_reader(self):
        u = _make_user('r', ROLE_READER)
        assert get_role_label(u) == ROLE_READER

    def test_get_role_label_analyst(self):
        u = _make_user('a', ROLE_ANALYST)
        assert get_role_label(u) == ROLE_ANALYST

    def test_get_role_label_editor(self):
        u = _make_user('e', ROLE_EDITOR)
        assert get_role_label(u) == ROLE_EDITOR

    def test_get_role_label_superuser(self):
        u = User.objects.create_superuser('su', password='p')
        assert get_role_label(u) == 'Суперпользователь'


class TestAccessControl(TestCase):
    def setUp(self):
        self.client = Client()
        self.reader = _make_user('reader2', ROLE_READER)
        self.analyst = _make_user('analyst2', ROLE_ANALYST)

    def _get(self, username, url_name, *args):
        self.client.force_login(User.objects.get(username=username))
        return self.client.get(reverse(url_name, args=args))

    def test_reader_blocked_from_builder(self):
        resp = self._get('reader2', 'builder:home')
        assert resp.status_code == 403

    def test_reader_blocked_from_analytics(self):
        resp = self._get('reader2', 'analytics:dashboard')
        assert resp.status_code == 403

    def test_analyst_can_access_builder(self):
        resp = self._get('analyst2', 'builder:home')
        assert resp.status_code == 200

    def test_analyst_can_access_analytics(self):
        resp = self._get('analyst2', 'analytics:dashboard')
        assert resp.status_code == 200

    def test_reader_can_access_search(self):
        resp = self._get('reader2', 'search:search')
        assert resp.status_code == 200

    def test_reader_can_access_norm_list(self):
        resp = self._get('reader2', 'knowledge:norm_list')
        assert resp.status_code == 200

    def test_profile_accessible(self):
        resp = self._get('reader2', 'accounts:profile')
        assert resp.status_code == 200

    def test_unauthenticated_redirected(self):
        resp = self.client.get(reverse('builder:home'))
        assert resp.status_code == 302
        assert '/accounts/login/' in resp['Location']
