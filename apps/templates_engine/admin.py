from django.contrib import admin
from .models import ШаблонДокумента, Переменная


class ПеременнаяInline(admin.TabularInline):
    model = Переменная
    extra = 1
    fields = ('ключ', 'подпись', 'тип_данных', 'обязательное', 'значение_по_умолчанию', 'порядок')


@admin.register(ШаблонДокумента)
class ШаблонДокументаAdmin(admin.ModelAdmin):
    list_display = ('название', 'тип', 'активен', 'создан')
    list_filter = ('тип', 'активен')
    search_fields = ('название', 'описание')
    inlines = [ПеременнаяInline]


@admin.register(Переменная)
class ПеременнаяAdmin(admin.ModelAdmin):
    list_display = ('шаблон', 'ключ', 'подпись', 'тип_данных', 'обязательное', 'порядок')
    list_filter = ('шаблон', 'тип_данных', 'обязательное')
    search_fields = ('ключ', 'подпись', 'шаблон__название')
    ordering = ('шаблон', 'порядок')
