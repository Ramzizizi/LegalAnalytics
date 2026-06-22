from django.db import models


class LegalBranch(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Отрасль права')
    description = models.TextField(blank=True, verbose_name='Описание')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Отрасль права'
        verbose_name_plural = 'Отрасли права'
        ordering = ['name']

    def __str__(self):
        return self.name
