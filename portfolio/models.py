from django.db import models
from django.utils.text import slugify
import datetime


class SiteConfig(models.Model):
    is_available = models.BooleanField(default=True)
    availability_note = models.CharField(max_length=200, default="Open to new opportunities")
    currently_building = models.CharField(max_length=300, blank=True,
                                          help_text="e.g. 'Audio ERP + POS system in Django'")
    currently_building_url = models.URLField(blank=True)
    resume = models.FileField(upload_to="resume/", blank=True, null=True,
                              help_text="Upload your CV/Resume (PDF)")
    photo = models.ImageField(upload_to="profile/", blank=True, null=True,
                              help_text="Professional headshot — displays in the hero section")

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class ProfilePhoto(models.Model):
    image    = models.ImageField(upload_to='profile/')
    caption  = models.CharField(max_length=100, blank=True)
    order    = models.PositiveIntegerField(default=0)
    is_active= models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Photo {self.order} — {self.caption or self.image.name}"


class Project(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        IN_PROGRESS = "in_progress", "In Progress"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    tagline = models.CharField(max_length=300)
    description = models.TextField()
    tech_stack = models.JSONField(default=list, help_text='e.g. ["Django", "PostgreSQL"]')
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("project_detail", kwargs={"slug": self.slug})


class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class WorkExperience(models.Model):
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.role} at {self.company}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject}"


class Appointment(models.Model):
    class TimeSlot(models.TextChoices):
        NINE = "09:00", "9:00 AM"
        ELEVEN = "11:00", "11:00 AM"
        TWO = "14:00", "2:00 PM"
        FOUR = "16:00", "4:00 PM"

    class Purpose(models.TextChoices):
        CONSULTATION = "consultation", "Technical Consultation"
        COLLABORATION = "collaboration", "Project Collaboration"
        MENTORSHIP = "mentorship", "Mentorship / Career Chat"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=200)
    email = models.EmailField()
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TimeSlot.choices)
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.CONSULTATION)
    message = models.TextField(blank=True, help_text="Anything you'd like to discuss in advance")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time_slot"]
        unique_together = [["date", "time_slot"]]

    def __str__(self):
        return f"{self.name} — {self.date} {self.time_slot}"

    @property
    def is_past(self):
        return self.date < datetime.date.today()


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        BOOK     = 'book',     'Book'
        TUTORIAL = 'tutorial', 'Tutorial / Video Course'
        ARTICLE  = 'article',  'Article'
        COURSE   = 'course',   'Online Course'
        VIDEO    = 'video',    'YouTube / Video'

    title         = models.CharField(max_length=200)
    author        = models.CharField(max_length=200, blank=True)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    url           = models.URLField(blank=True)
    description   = models.TextField(blank=True)
    cover         = models.ImageField(upload_to='resources/', blank=True, null=True)
    is_featured   = models.BooleanField(default=False)
    date_consumed = models.DateField(null=True, blank=True, help_text='When you read/watched it')
    rating        = models.PositiveSmallIntegerField(null=True, blank=True, help_text='1–5 stars')

    class Meta:
        ordering = ['-date_consumed', 'resource_type']

    def __str__(self):
        return f'{self.title} ({self.get_resource_type_display()})'


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.CharField(max_length=400)
    content = models.TextField(help_text="HTML content — write or paste from an editor")
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    external_url = models.URLField(blank=True, help_text="Link to Medium/Dev.to if cross-posted")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("writing_detail", kwargs={"slug": self.slug})
