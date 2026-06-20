from django.contrib import admin
from .models import СгенерированныйДокумент


@admin.register(СгенерированныйДокумент)
class СгенерированныйДокументAdmin(admin.ModelAdmin):
    list_display = ('шаблон', 'контрагент', 'автор', 'статус', 'создан')
    list_filter = ('статус', 'шаблон__тип', 'создан')
    search_fields = ('шаблон__название', 'контрагент__наименование', 'автор__username')
    readonly_fields = ('создан', 'изменён', 'значения', 'ошибка')
    ordering = ('-создан',)
    date_hierarchy = 'создан'
