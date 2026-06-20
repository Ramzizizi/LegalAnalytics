"""Динамическая форма: поля строятся из переменных выбранного шаблона."""
import datetime

from django import forms
from apps.catalog.models import Контрагент
from apps.templates_engine.models import ШаблонДокумента, Переменная


class ДинамическаяФорма(forms.Form):
    """Форма с полями, динамически сгенерированными из переменных шаблона."""

    контрагент = forms.ModelChoiceField(
        queryset=Контрагент.objects.all(),
        label='Контрагент',
        empty_label='— Выберите контрагента —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, шаблон: ШаблонДокумента, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.шаблон = шаблон

        for переменная in шаблон.переменные.order_by('порядок', 'ключ'):
            field = self._сделать_поле(переменная)
            self.fields[переменная.ключ] = field

    def _сделать_поле(self, переменная: Переменная) -> forms.Field:
        общие = {
            'label': переменная.подпись,
            'required': переменная.обязательное,
            'initial': переменная.значение_по_умолчанию or None,
        }

        if переменная.тип_данных == 'date':
            return forms.DateField(
                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                input_formats=['%Y-%m-%d', '%d.%m.%Y'],
                **общие,
            )
        if переменная.тип_данных == 'decimal':
            return forms.DecimalField(
                max_digits=15,
                decimal_places=2,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                **общие,
            )
        if переменная.тип_данных == 'int':
            return forms.IntegerField(
                widget=forms.NumberInput(attrs={'class': 'form-control'}),
                **общие,
            )
        return forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            max_length=500,
            **общие,
        )

    def получить_контекст(self) -> dict:
        """Возвращает context для docxtpl: поля формы + авто-поля контрагента."""
        data = self.cleaned_data.copy()
        контрагент = data.pop('контрагент')

        data.update({
            'contragent_name': контрагент.наименование,
            'contragent_inn': контрагент.инн,
            'contragent_kpp': контрагент.кпп,
            'contragent_address': контрагент.адрес,
        })

        for key, val in list(data.items()):
            if isinstance(val, datetime.date):
                data[key] = val.strftime('%d.%m.%Y')
            elif val is None:
                data[key] = ''

        return data
