import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.catalog.models import LegalBranch
from apps.knowledge.models import Norm, CourtCase

User = get_user_model()


class TestBuilder(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='builder_user', password='p')
        self.client.login(username='builder_user', password='p')

        self.branch = LegalBranch.objects.create(name='Гражданское', slug='civil-b')
        self.norm = Norm.objects.create(
            title='ГК РФ ст. 309', norm_type='code',
            article='ст. 309 ГК РФ', text='Обязательства должны исполняться надлежащим образом.',
            branch=self.branch,
        )
        self.case = CourtCase.objects.create(
            court='Арбитражный суд', case_number='А53-100/2024',
            decision_date='2024-03-01', thesis='Тест builder', branch=self.branch,
        )

    def test_builder_home(self):
        resp = self.client.get(reverse('builder:home'))
        assert resp.status_code == 200
        assert 'Конструктор' in resp.content.decode()

    def test_builder_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse('builder:home'))
        assert resp.status_code == 302

    def test_add_norm_to_basket(self):
        resp = self.client.post(
            reverse('builder:basket_add', args=['norm', self.norm.pk]),
            {'next': reverse('builder:home')},
        )
        assert resp.status_code == 302
        basket = self.client.session['basket']
        assert self.norm.pk in basket['norms']

    def test_add_case_to_basket(self):
        resp = self.client.post(
            reverse('builder:basket_add', args=['case', self.case.pk]),
            {'next': reverse('builder:home')},
        )
        assert resp.status_code == 302
        basket = self.client.session['basket']
        assert self.case.pk in basket['cases']

    def test_add_norm_idempotent(self):
        url = reverse('builder:basket_add', args=['norm', self.norm.pk])
        self.client.post(url, {'next': '/'})
        self.client.post(url, {'next': '/'})
        basket = self.client.session['basket']
        assert basket['norms'].count(self.norm.pk) == 1

    def test_remove_norm_from_basket(self):
        self.client.post(
            reverse('builder:basket_add', args=['norm', self.norm.pk]),
            {'next': '/'},
        )
        self.client.post(reverse('builder:basket_remove', args=['norm', self.norm.pk]))
        basket = self.client.session['basket']
        assert self.norm.pk not in basket['norms']

    def test_clear_basket(self):
        self.client.post(reverse('builder:basket_add', args=['norm', self.norm.pk]), {'next': '/'})
        self.client.post(reverse('builder:basket_add', args=['case', self.case.pk]), {'next': '/'})
        self.client.post(reverse('builder:basket_clear'))
        basket = self.client.session['basket']
        assert basket['norms'] == []
        assert basket['cases'] == []

    def test_basket_shown_on_builder_page(self):
        self.client.post(reverse('builder:basket_add', args=['norm', self.norm.pk]), {'next': '/'})
        resp = self.client.get(reverse('builder:home'))
        assert resp.status_code == 200
        assert 'ст. 309' in resp.content.decode()

    def test_export_docx(self):
        self.client.post(reverse('builder:basket_add', args=['norm', self.norm.pk]), {'next': '/'})
        self.client.post(reverse('builder:basket_add', args=['case', self.case.pk]), {'next': '/'})
        resp = self.client.post(reverse('builder:export'), {
            'title': 'Тестовое заключение',
            'question': 'Как исполняются обязательства?',
            'conclusion': 'Обязательства исполняются надлежащим образом.',
        })
        assert resp.status_code == 200
        assert resp['Content-Type'] == (
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        assert 'attachment' in resp['Content-Disposition']
        assert len(resp.content) > 1000

    def test_export_empty_basket(self):
        resp = self.client.post(reverse('builder:export'), {
            'title': 'Без материалов',
            'question': '',
            'conclusion': 'Заключение.',
        })
        assert resp.status_code == 200
        assert resp['Content-Type'] == (
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
