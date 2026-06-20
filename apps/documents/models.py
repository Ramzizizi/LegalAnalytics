"""Модель сгенерированного документа: связь шаблон+автор+контрагент, файлы и статус."""
from django.db import models
from django.contrib.auth.models import User
from apps.catalog.models import Контрагент
from apps.templates_engine.models import ШаблонДокумента


class СгенерированныйДокумент(models.Model):
    СТАТУС_ВЫБОР = [
        ('черновик', 'Черновик'),
        ('готов', 'Готов'),
        ('ошибка', 'Ошибка генерации'),
    ]

    шаблон = models.ForeignKey(
        ШаблонДокумента, on_delete=models.PROTECT,
        related_name='документы', verbose_name='Шаблон'
    )
    автор = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='документы', verbose_name='Автор'
    )
    контрагент = models.ForeignKey(
        Контрагент, on_delete=models.PROTECT,
        related_name='документы', verbose_name='Контрагент'
    )
    значения = models.JSONField('Значения переменных', default=dict)
    файл_docx = models.FileField('Файл .docx', upload_to='documents/docx/', blank=True)
    файл_pdf = models.FileField('Файл .pdf', upload_to='documents/pdf/', blank=True)
    статус = models.CharField('Статус', max_length=10, choices=СТАТУС_ВЫБОР, default='черновик')
    ошибка = models.TextField('Сообщение об ошибке', blank=True)
    создан = models.DateTimeField(auto_now_add=True)
    изменён = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сгенерированный документ'
        verbose_name_plural = 'Сгенерированные документы'
        ordering = ['-создан']

    def __str__(self):
        return f'{self.шаблон.название} — {self.контрагент.наименование} ({self.создан:%d.%m.%Y})'
