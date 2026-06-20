"""Справочники каталога: контрагенты (с валидацией ИНН) и юристы."""
from django.db import models
from django.contrib.auth.models import User
from .validators import валидатор_инн


class Контрагент(models.Model):
    ТИП_ВЫБОР = [
        ('юр', 'Юридическое лицо'),
        ('физ', 'Физическое лицо / ИП'),
    ]

    наименование = models.CharField('Наименование', max_length=255)
    тип = models.CharField('Тип', max_length=3, choices=ТИП_ВЫБОР, default='юр')
    инн = models.CharField('ИНН', max_length=12, validators=[валидатор_инн])
    кпп = models.CharField('КПП', max_length=9, blank=True)
    адрес = models.TextField('Юридический адрес', blank=True)
    телефон = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    создан = models.DateTimeField(auto_now_add=True)
    изменён = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
        ordering = ['наименование']

    def __str__(self):
        return f'{self.наименование} (ИНН {self.инн})'


class Юрист(models.Model):
    пользователь = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='юрист', verbose_name='Пользователь'
    )
    должность = models.CharField('Должность', max_length=100, blank=True)
    телефон = models.CharField('Телефон', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Юрист'
        verbose_name_plural = 'Юристы'

    def __str__(self):
        return self.пользователь.get_full_name() or self.пользователь.username
