from django.contrib import admin
from .models import JobOpening, TeamMember

@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'is_active', 'created_at')
    list_filter = ('job_type', 'is_active', 'location')
    search_fields = ('title', 'description', 'requirements')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'designation', 'expertise_tags')
