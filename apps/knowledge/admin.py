from django.contrib import admin
from .models import Norm, CourtCase, LegalOpinion


@admin.register(Norm)
class NormAdmin(admin.ModelAdmin):
    list_display = ['title', 'norm_type', 'article', 'branch', 'effective_date']
    list_filter = ['norm_type', 'branch']
    search_fields = ['title', 'article', 'text']
    autocomplete_fields = ['branch']


@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'court', 'decision_date', 'branch', 'thesis']
    list_filter = ['branch', 'decision_date']
    search_fields = ['case_number', 'court', 'thesis', 'text']
    filter_horizontal = ['related_norms']


@admin.register(LegalOpinion)
class LegalOpinionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'text']
    filter_horizontal = ['related_norms', 'related_cases']
    readonly_fields = ['created_at']
