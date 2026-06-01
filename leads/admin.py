from django.contrib import admin
from django.utils.html import format_html
from .models import Lead, NewsletterSubscriber, HappyFamily, Job

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'property_link', 'source', 'status', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Lead Details', {
            'fields': ('interested_property', 'source', 'status', 'budget', 'message')
        }),
        ('Interest Details', {
            'fields': ('preferred_property_type', 'preferred_locality', 'preferred_bedrooms', 'purchase_timeline'),
            'classes': ('collapse',)
        }),
        ('Communication', {
            'fields': ('call_attempts', 'last_contacted', 'follow_up_date', 'notes')
        }),
        ('Tracking', {
            'fields': ('ip_address', 'user_agent', 'referring_url', 'utm_source', 'utm_medium', 'utm_campaign'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def property_link(self, obj):
        if obj.interested_property:
            return format_html('<a href="/admin/properties/property/{}/change/">{}</a>', 
                             obj.interested_property.id, obj.interested_property.title)
        return "-"
    property_link.short_description = 'Property'
    
    actions = ['mark_contacted', 'mark_qualified']
    
    def mark_contacted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='contacted', last_contacted=timezone.now())
        self.message_user(request, f'{updated} leads marked as contacted.')
    mark_contacted.short_description = "Mark as contacted"
    
    def mark_qualified(self, request, queryset):
        updated = queryset.update(status='qualified')
        self.message_user(request, f'{updated} leads marked as qualified.')
    mark_qualified.short_description = "Mark as qualified"

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']

@admin.register(HappyFamily)
class HappyFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'rating', 'is_active', 'created_at')
    list_filter = ('is_active', 'rating')
    search_fields = ('name', 'location', 'content')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'type', 'is_active', 'created_at')
    list_filter = ('is_active', 'type')
    search_fields = ('title', 'description', 'requirements')