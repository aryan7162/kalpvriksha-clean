from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Lead(models.Model):
    LEAD_SOURCES = (
        ('property_page', 'Property Page'),
        ('contact_form', 'Contact Form'),
        ('homepage', 'Homepage'),
        ('blog', 'Blog'),
        ('landing_page', 'Landing Page'),
        ('social_media', 'Social Media'),
        ('referral', 'Referral'),
    )
    
    LEAD_STATUS = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal_sent', 'Proposal Sent'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('junk', 'Junk'),
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=15, db_index=True)
    
    # Lead Details
    source = models.CharField(max_length=20, choices=LEAD_SOURCES, default='contact_form')
    status = models.CharField(max_length=20, choices=LEAD_STATUS, default='new')
    interested_property = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    message = models.TextField()
    
    # Interest
    preferred_property_type = models.CharField(max_length=50, blank=True)
    preferred_locality = models.CharField(max_length=100, blank=True)
    preferred_bedrooms = models.IntegerField(blank=True, null=True)
    purchase_timeline = models.CharField(max_length=50, blank=True)
    
    # Tracking
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    referring_url = models.URLField(blank=True, null=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    # Communication
    call_attempts = models.PositiveIntegerField(default=0)
    last_contacted = models.DateTimeField(blank=True, null=True)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['phone', 'status']),
        ]
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    

class HappyFamily(models.Model):
    name = models.CharField(max_length=200, help_text="Family name or Client name")
    location = models.CharField(max_length=200, blank=True, help_text="e.g., Koregaon Park, Pune")
    content = models.TextField(verbose_name="Testimonial Text")
    photo = models.ImageField(upload_to='happy_families/photos/', blank=True, null=True)
    video_file = models.FileField(upload_to='happy_families/videos/', blank=True, null=True, help_text="Upload testimonial video (MP4)")
    document = models.FileField(upload_to='happy_families/docs/', blank=True, null=True, help_text="Optional appreciation letter/document")
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Happy Family"
        verbose_name_plural = "Happy Families"
        ordering = ['-created_at']

    def __str__(self):
        return f"Family: {self.name}"

class Job(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    type = models.CharField(max_length=100, choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract')])
    description = models.TextField()
    requirements = models.TextField(help_text="Enter requirements separated by new lines")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_requirements_list(self):
        return [r.strip() for r in self.requirements.split('\n') if r.strip()]

    def __str__(self):
        return self.title