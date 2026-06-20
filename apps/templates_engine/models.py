"""Модели движка шаблонов: Word-шаблон документа и его переменные."""
from django.db import models


class ШаблонДокумента(models.Model):
    ТИП_ВЫБОР = [
        ('услуги', 'Договор оказания услуг'),
        ('поставка', 'Договор поставки'),
        ('претензия', 'Претензия'),
        ('доверенность', 'Доверенность'),
        ('иск', 'Исковое заявление'),
        ('иное', 'Иное'),
    ]

    название = models.CharField('Название', max_length=255)
    тип = models.CharField('Тип документа', max_length=20, choices=ТИП_ВЫБОР, default='иное')
    описание = models.TextField('Описание', blank=True)
    файл = models.FileField('Файл шаблона (.docx)', upload_to='templates/')
    активен = models.BooleanField('Активен', default=True)
    создан = models.DateTimeField(auto_now_add=True)
    изменён = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Шаблон документа'
        verbose_name_plural = 'Шаблоны документов'
        ordering = ['название']

    def __str__(self):
        return self.название


class Переменная(models.Model):
    ТИП_ДАННЫХ = [
        ('str', 'Текст'),
        ('date', 'Дата'),
        ('decimal', 'Сумма'),
        ('int', 'Целое число'),
        ('choice', 'Выбор из списка'),
    ]

    шаблон = models.ForeignKey(
        ШаблонДокумента, on_delete=models.CASCADE,
        related_name='переменные', verbose_name='Шаблон'
    )
    ключ = models.CharField('Ключ (тег в шаблоне)', max_length=100)
    подпись = models.CharField('Подпись в форме', max_length=255)
    тип_данных = models.CharField('Тип данных', max_length=10, choices=ТИП_ДАННЫХ, default='str')
    обязательное = models.BooleanField('Обязательное', default=True)
    значение_по_умолчанию = models.CharField('Значение по умолчанию', max_length=255, blank=True)
    порядок = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Переменная'
        verbose_name_plural = 'Переменные'
        ordering = ['порядок', 'ключ']
        unique_together = [('шаблон', 'ключ')]

    def __str__(self):
        return f'{self.шаблон.название} → {self.ключ}'
