from django.db import models
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from apps.catalog.models import LegalBranch

User = get_user_model()

NORM_TYPE_CHOICES = [
    ('law', 'Федеральный закон'),
    ('code', 'Кодекс'),
    ('decree', 'Указ Президента'),
    ('resolution', 'Постановление Правительства'),
    ('order', 'Приказ'),
    ('other', 'Иное'),
]


class Norm(models.Model):
    title = models.CharField(max_length=500, verbose_name='Название')
    norm_type = models.CharField(max_length=20, choices=NORM_TYPE_CHOICES, default='law', verbose_name='Вид НПА')
    article = models.CharField(max_length=100, blank=True, verbose_name='Статья')
    text = models.TextField(verbose_name='Текст нормы')
    source = models.CharField(max_length=500, blank=True, verbose_name='Источник')
    effective_date = models.DateField(null=True, blank=True, verbose_name='Дата вступления в силу')
    branch = models.ForeignKey(
        LegalBranch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='norms', verbose_name='Отрасль права'
    )
    tags = TaggableManager(blank=True, verbose_name='Теги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        verbose_name = 'Норма'
        verbose_name_plural = 'Нормы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CourtCase(models.Model):
    court = models.CharField(max_length=300, verbose_name='Суд')
    case_number = models.CharField(max_length=100, verbose_name='Номер дела')
    decision_date = models.DateField(verbose_name='Дата решения')
    thesis = models.CharField(max_length=500, verbose_name='Тезис')
    text = models.TextField(blank=True, verbose_name='Текст / ссылка')
    branch = models.ForeignKey(
        LegalBranch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='court_cases', verbose_name='Отрасль права'
    )
    related_norms = models.ManyToManyField(
        Norm, blank=True, related_name='court_cases', verbose_name='Связанные нормы'
    )
    tags = TaggableManager(blank=True, verbose_name='Теги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        verbose_name = 'Судебная практика'
        verbose_name_plural = 'Судебная практика'
        ordering = ['-decision_date']

    def __str__(self):
        return f'{self.case_number} — {self.thesis[:60]}'


class LegalOpinion(models.Model):
    title = models.CharField(max_length=500, verbose_name='Тема заключения')
    text = models.TextField(verbose_name='Текст заключения')
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='opinions', verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    related_norms = models.ManyToManyField(
        Norm, blank=True, related_name='opinions', verbose_name='Связанные нормы'
    )
    related_cases = models.ManyToManyField(
        CourtCase, blank=True, related_name='opinions', verbose_name='Связанная практика'
    )
    tags = TaggableManager(blank=True, verbose_name='Теги')
    is_public = models.BooleanField(default=False, verbose_name='Общедоступное')

    class Meta:
        verbose_name = 'Правовое заключение'
        verbose_name_plural = 'Правовые заключения'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
