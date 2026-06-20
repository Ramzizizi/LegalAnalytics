from django.contrib import admin
from .models import Контрагент, Юрист


@admin.register(Контрагент)
class КонтрагентAdmin(admin.ModelAdmin):
    list_display = ('наименование', 'тип', 'инн', 'кпп', 'телефон', 'email')
    list_filter = ('тип',)
    search_fields = ('наименование', 'инн', 'кпп')
    ordering = ('наименование',)


@admin.register(Юрист)
class ЮристAdmin(admin.ModelAdmin):
    list_display = ('пользователь', 'должность', 'телефон')
    search_fields = ('пользователь__username', 'пользователь__last_name', 'должность')
    raw_id_fields = ('пользователь',)
