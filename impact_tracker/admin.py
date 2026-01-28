from django.contrib import admin
from .models import SDGGoal, Activity, SDGImpact, InstitutionMetric


@admin.register(SDGGoal)
class SDGGoalAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_type', 'lead_author', 'date_created', 'ai_classified')
    list_filter = ('activity_type', 'ai_classified', 'date_created')
    search_fields = ('title', 'description', 'lead_author__username')
    readonly_fields = ('date_created', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'activity_type')
        }),
        ('Metadata', {
            'fields': ('lead_author', 'evidence_file', 'ai_classified')
        }),
        ('Timestamps', {
            'fields': ('date_created', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SDGImpact)
class SDGImpactAdmin(admin.ModelAdmin):
    list_display = ('activity', 'sdg_goal', 'score', 'created_at')
    list_filter = ('sdg_goal', 'score', 'created_at')
    search_fields = ('activity__title', 'justification')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstitutionMetric)
class InstitutionMetricAdmin(admin.ModelAdmin):
    list_display = ('university_name', 'year', 'sdg_goal', 'score', 'total_activities')
    list_filter = ('year', 'sdg_goal', 'university_name')
    search_fields = ('university_name',)
    readonly_fields = ('created_at', 'updated_at')
