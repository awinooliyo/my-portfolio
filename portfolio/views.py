from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
import datetime

from .models import Project, SkillCategory, WorkExperience, ContactMessage, Appointment, BlogPost, Resource, SiteConfig, ProfilePhoto


def home(request):
    projects = Project.objects.filter(featured=True).order_by("order")
    skill_categories = SkillCategory.objects.prefetch_related("skills").all()
    experiences = WorkExperience.objects.all()
    blog_posts        = BlogPost.objects.filter(is_published=True)[:3]
    profile_photos    = list(ProfilePhoto.objects.filter(is_active=True))
    featured_resources = Resource.objects.filter(is_featured=True)[:4]

    booked_slots = set(
        Appointment.objects.filter(
            date__gte=datetime.date.today(),
            status__in=["pending", "confirmed"],
        ).values_list("date", "time_slot")
    )

    context = {
        "projects": projects,
        "skill_categories": skill_categories,
        "experiences": experiences,
        "blog_posts": blog_posts,
        "booked_slots": booked_slots,
        "time_slots": Appointment.TimeSlot.choices,
        "purposes": Appointment.Purpose.choices,
        "today": datetime.date.today().isoformat(),
        "featured_resources": featured_resources,
        "profile_photos": profile_photos,
    }
    return render(request, "portfolio/home.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    other_projects = Project.objects.filter(featured=True).exclude(pk=project.pk)[:3]
    return render(request, "portfolio/project_detail.html", {
        "project": project,
        "other_projects": other_projects,
    })


def blog_list(request):
    tab = request.GET.get("tab", "articles")
    posts     = BlogPost.objects.filter(is_published=True)
    resources = Resource.objects.all()

    if tab == "books":
        resources = resources.filter(resource_type="book")
    elif tab == "tutorials":
        resources = resources.filter(resource_type__in=["tutorial", "video", "course"])
    elif tab == "articles":
        resources = resources.filter(resource_type="article")

    tabs = [
        ("Articles", "articles"),
        ("Books", "books"),
        ("Tutorials & Courses", "tutorials"),
    ]
    return render(request, "portfolio/blog_list.html", {
        "posts": posts,
        "resources": resources,
        "active_tab": tab,
        "tabs": tabs,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "portfolio/blog_detail.html", {"post": post})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("message", "").strip()

        if name and email and subject and body:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=body)
            messages.success(request, "Message sent! I'll get back to you soon.")
        else:
            messages.error(request, "Please fill in all fields.")

    return redirect("home")


def resume(request):
    try:
        config = SiteConfig.objects.get(pk=1)
    except SiteConfig.DoesNotExist:
        config = None
    return render(request, "portfolio/resume.html", {"site_config": config})


def book_appointment(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        date_str = request.POST.get("date", "").strip()
        time_slot = request.POST.get("time_slot", "").strip()
        purpose = request.POST.get("purpose", "consultation").strip()
        note = request.POST.get("message", "").strip()

        try:
            date = datetime.date.fromisoformat(date_str)
            if date < datetime.date.today():
                raise ValueError("Past date")
        except (ValueError, TypeError):
            messages.error(request, "Please choose a valid future date.")
            return redirect("home")

        if not all([name, email, time_slot]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("home")

        if Appointment.objects.filter(date=date, time_slot=time_slot,
                                      status__in=["pending", "confirmed"]).exists():
            messages.error(request, "That slot is already taken — please pick another time.")
            return redirect("home")

        Appointment.objects.create(
            name=name, email=email, date=date,
            time_slot=time_slot, purpose=purpose, message=note,
        )
        messages.success(request,
                         f"Booking request sent for {date.strftime('%B %d')} at "
                         f"{dict(Appointment.TimeSlot.choices)[time_slot]}. "
                         "I'll confirm by email.")

    return redirect("home")
