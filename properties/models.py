from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Sublocation(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='sublocations')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)

    class Meta:
        unique_together = ('city', 'slug')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.city.name}"

class Builder(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    logo = models.ImageField(upload_to='builders/logos/')
    description = models.TextField(blank=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    projects_completed = models.PositiveIntegerField(default=0)
    website = models.URLField(blank=True)
    
    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Property(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('penthouse', 'Penthouse'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),
    )
    
    # Basic Information
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    description = models.TextField()
    short_description = models.TextField(max_length=500, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    price_display = models.CharField(max_length=100, blank=True, help_text="Custom price display (e.g. 1.1cr - 1.5cr). If empty, numerical price will be shown.")
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    booking_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hide_price = models.BooleanField(default=False, help_text="Show 'Price on Request' instead of the actual price")
    
    # Property Details
    total_land_parcel = models.CharField(max_length=100, blank=True, help_text="e.g. 5 Acres")
    construction_type = models.CharField(max_length=100, blank=True, help_text="e.g. Mivan Construction")
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    carpet_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    floor_no = models.IntegerField(blank=True, null=True)
    total_floors = models.IntegerField(blank=True, null=True)
    
    # Location
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='properties')
    sublocation = models.ForeignKey(Sublocation, on_delete=models.SET_NULL, null=True, related_name='properties')
    pincode = models.CharField(max_length=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Media
    main_image = models.ImageField(upload_to='properties/main/%Y/%m/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    virtual_tour_url = models.URLField(blank=True, null=True)
    floor_plan = models.ImageField(upload_to='properties/floorplans/%Y/%m/', blank=True, null=True)
    
    # Builder/Developer
    builder = models.ForeignKey(Builder, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    builder_name = models.CharField(max_length=200, blank=True)
    builder_logo = models.ImageField(upload_to='builders/logos/', blank=True, null=True)
    rera_number = models.CharField(max_length=50, blank=True, null=True, default='A041262504685')
    possession_date = models.DateField(blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO Title (max 70 chars)")
    meta_description = models.TextField(max_length=160, blank=True, help_text="SEO Description (max 160 chars)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    canonical_url = models.URLField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_urgent_sale = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    inquiries_count = models.PositiveIntegerField(default=0)
    
    # Amenities
    amenities = models.ManyToManyField('Amenity', blank=True, related_name='properties')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'status']),
            models.Index(fields=['sublocation', 'status']),
            models.Index(fields=['price', 'status']),
            models.Index(fields=['area_sqft', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'slug': self.slug})
    
    def get_canonical_url(self):
        return self.canonical_url or self.get_absolute_url()
    
    def __str__(self):
        return self.title

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='gallery', null=True, blank=True)
    image = models.ImageField(upload_to='properties/gallery/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, help_text="SEO alt text")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.caption or f"Image {self.id}"

class PropertyConfiguration(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='configurations')
    name = models.CharField(max_length=100, help_text="e.g. 2BHK Type A")
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    carpet_area = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_display = models.CharField(max_length=100, blank=True, help_text="e.g. 1.1cr - 1.5cr")
    hide_price = models.BooleanField(default=False)
    floor_plan = models.ImageField(upload_to='properties/configurations/%Y/%m/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.property.title} - {self.name}"