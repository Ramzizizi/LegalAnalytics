from django.contrib import admin
from .models import LegalBranch


@admin.register(LegalBranch)
class LegalBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
