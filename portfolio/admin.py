from django.contrib import admin
from .models import (
    SiteConfig, ProfilePhoto, Project, SkillCategory, Skill,
    WorkExperience, ContactMessage, Appointment, BlogPost, Resource,
)


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Availability", {"fields": ("is_available", "availability_note")}),
        ("Current Work", {"fields": ("currently_building", "currently_building_url")}),
        ("Resume", {"fields": ("resume",)}),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ("name", "order")


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    inlines = [SkillInline]
    list_display = ("name", "order")
    list_editable = ("order",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "featured", "order")
    list_editable = ("featured", "order", "status")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "tagline", "description", "image")}),
        ("Links", {"fields": ("github_url", "live_url")}),
        ("Tech", {"fields": ("tech_stack",)}),
        ("Display", {"fields": ("featured", "order", "status")}),
    )


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "company", "start_date", "is_current")
    list_editable = ("is_current",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_editable = ("is_read",)
    readonly_fields = ("name", "email", "subject", "message", "created_at")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date", "time_slot", "purpose", "status")
    list_editable = ("status",)
    list_filter = ("status", "purpose", "date")
    readonly_fields = ("name", "email", "date", "time_slot", "purpose", "message", "created_at")


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('image', 'caption', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'author', 'rating', 'is_featured', 'date_consumed')
    list_editable = ('is_featured', 'rating')
    list_filter = ('resource_type', 'is_featured')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "excerpt", "content", "cover_image")}),
        ("Publishing", {"fields": ("is_published", "published_at", "external_url")}),
    )
