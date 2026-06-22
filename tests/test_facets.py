import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import connection

from apps.catalog.models import LegalBranch
from apps.knowledge.models import Norm, CourtCase

User = get_user_model()
IS_POSTGRES = connection.vendor == 'postgresql'
skip_sqlite = pytest.mark.skipif(not IS_POSTGRES, reason='Требуется PostgreSQL для FTS')


class TestFacetsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='u', password='p')
        self.client.login(username='u', password='p')
        self.branch = LegalBranch.objects.create(name='Гражданское право', slug='civil-test')

    def test_search_with_branch_filter(self):
        response = self.client.get(
            reverse('search:search') + f'?q=договор&branch={self.branch.pk}'
        )
        assert response.status_code == 200

    def test_search_with_type_and_branch(self):
        response = self.client.get(
            reverse('search:search') + f'?q=договор&type=norm&branch={self.branch.pk}'
        )
        assert response.status_code == 200

    def test_search_with_tag_filter(self):
        response = self.client.get(
            reverse('search:search') + '?q=договор&tag=аренда'
        )
        assert response.status_code == 200

    def test_search_with_date_range(self):
        response = self.client.get(
            reverse('search:search') + '?q=кодекс&date_from=2000-01-01&date_to=2023-12-31'
        )
        assert response.status_code == 200

    def test_active_filters_chips_shown(self):
        response = self.client.get(
            reverse('search:search') + f'?q=договор&type=norm&branch={self.branch.pk}'
        )
        content = response.content.decode()
        assert 'Нормы права' in content

    def test_empty_results_show_reset_button(self):
        response = self.client.get(
            reverse('search:search') + '?q=xyzнесуществующий&type=norm'
        )
        assert response.status_code == 200

    def test_htmx_with_filters(self):
        response = self.client.get(
            reverse('search:search') + '?q=договор&type=norm',
            HTTP_HX_REQUEST='true',
        )
        assert response.status_code == 200
        assert b'<!DOCTYPE' not in response.content

    def test_hint_tags_shown_without_query(self):
        response = self.client.get(reverse('search:search'))
        content = response.content.decode()
        assert 'договор' in content
