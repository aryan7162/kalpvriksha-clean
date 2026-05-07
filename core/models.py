from django.db import models

class JobOpening(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=[
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Freelance', 'Freelance'),
        ('Internship', 'Internship'),
    ], default='Full-time')
    description = models.TextField()
    requirements = models.TextField(help_text="Enter requirements separated by new lines")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def type(self):
        return self.job_type

    def get_requirements_list(self):
        return [req.strip() for req in self.requirements.split('\n') if req.strip()]

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/')
    linkedin = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    expertise_tags = models.CharField(max_length=255, help_text="Comma separated tags", blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_expertise_list(self):
        return [tag.strip() for tag in self.expertise_tags.split(',') if tag.strip()]
