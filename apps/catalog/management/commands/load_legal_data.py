import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.catalog.models import LegalBranch
from apps.knowledge.models import Norm, CourtCase, LegalOpinion

DATA_DIR = Path(__file__).resolve().parents[4] / 'data'
User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузить демо-данные в базу (идемпотентно)'

    def handle(self, *args, **options):
        self._load_branches()
        self._load_norms()
        self._load_cases()
        self._load_opinions()
        self.stdout.write(self.style.SUCCESS('Демо-данные загружены.'))

    def _load_branches(self):
        data = self._read('branches.json')
        for item in data:
            LegalBranch.objects.update_or_create(
                slug=item['slug'],
                defaults={'name': item['name'], 'description': item.get('description', '')},
            )
        self.stdout.write(f'  Отрасли права: {len(data)}')

    def _load_norms(self):
        data = self._read('norms.json')
        count = 0
        for item in data:
            branch = LegalBranch.objects.filter(slug=item.get('branch_slug')).first()
            norm, created = Norm.objects.update_or_create(
                article=item['article'],
                defaults={
                    'title': item['title'],
                    'norm_type': item.get('norm_type', 'other'),
                    'text': item['text'],
                    'source': item.get('source', ''),
                    'effective_date': item.get('effective_date') or None,
                    'branch': branch,
                },
            )
            if item.get('tags'):
                norm.tags.set(item['tags'])
            if created:
                count += 1
        self.stdout.write(f'  Нормы: {Norm.objects.count()} (добавлено {count})')

    def _load_cases(self):
        data = self._read('cases.json')
        count = 0
        for item in data:
            branch = LegalBranch.objects.filter(slug=item.get('branch_slug')).first()
            case, created = CourtCase.objects.update_or_create(
                case_number=item['case_number'],
                defaults={
                    'court': item['court'],
                    'decision_date': item['decision_date'],
                    'thesis': item['thesis'],
                    'text': item.get('text', ''),
                    'branch': branch,
                },
            )
            if item.get('tags'):
                case.tags.set(item['tags'])
            if item.get('related_norm_articles'):
                norms = Norm.objects.filter(article__in=item['related_norm_articles'])
                case.related_norms.set(norms)
            if created:
                count += 1
        self.stdout.write(f'  Судебная практика: {CourtCase.objects.count()} (добавлено {count})')

    def _load_opinions(self):
        data = self._read('opinions.json')
        user = User.objects.filter(is_superuser=True).first()
        count = 0
        for item in data:
            opinion, created = LegalOpinion.objects.update_or_create(
                title=item['title'],
                defaults={
                    'text': item['text'],
                    'author': user,
                    'is_public': item.get('is_public', False),
                },
            )
            if item.get('tags'):
                opinion.tags.set(item['tags'])
            if item.get('related_norm_articles'):
                norms = Norm.objects.filter(article__in=item['related_norm_articles'])
                opinion.related_norms.set(norms)
            if item.get('related_case_numbers'):
                cases = CourtCase.objects.filter(case_number__in=item['related_case_numbers'])
                opinion.related_cases.set(cases)
            if created:
                count += 1
        self.stdout.write(f'  Заключения: {LegalOpinion.objects.count()} (добавлено {count})')

    @staticmethod
    def _read(filename):
        path = DATA_DIR / filename
        with open(path, encoding='utf-8') as f:
            return json.load(f)
