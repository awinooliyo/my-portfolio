from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import datetime

from .models import Project, SkillCategory, ContactMessage, Appointment, BlogPost, Resource, SiteConfig, ProfilePhoto


def home(request):
    from .models import WorkExperience
    projects = Project.objects.filter(featured=True).order_by("order")
    skill_categories = SkillCategory.objects.prefetch_related("skills").all()
    experiences = WorkExperience.objects.all()
    blog_posts = BlogPost.objects.filter(is_published=True)[:3]
    profile_photos = list(ProfilePhoto.objects.filter(is_active=True))
    featured_resources = Resource.objects.filter(is_featured=True)[:3]

    context = {
        "projects": projects,
        "skill_categories": skill_categories,
        "experiences": experiences,
        "blog_posts": blog_posts,
        "featured_resources": featured_resources,
        "profile_photos": profile_photos,
        "hobbies": HOBBIES,
    }
    return render(request, "portfolio/home.html", context)


def projects_list(request):
    status = request.GET.get("status", "")
    projects = Project.objects.all()
    if status in ("completed", "in_progress", "archived"):
        projects = projects.filter(status=status)
    return render(request, "portfolio/projects_list.html", {
        "projects": projects,
        "active_status": status,
    })


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    other_projects = Project.objects.filter(featured=True).exclude(pk=project.pk)[:3]
    return render(request, "portfolio/project_detail.html", {
        "project": project,
        "other_projects": other_projects,
    })


def writing_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, "portfolio/writing_list.html", {"posts": posts})


def writing_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "portfolio/writing_detail.html", {"post": post})


def library(request):
    resource_type = request.GET.get("type", "")
    resources = Resource.objects.all()
    if resource_type in ("book", "tutorial", "article", "course", "video"):
        resources = resources.filter(resource_type=resource_type)
    return render(request, "portfolio/library.html", {
        "resources": resources,
        "active_type": resource_type,
    })


def process(request):
    booked_slots = set(
        Appointment.objects.filter(
            date__gte=datetime.date.today(),
            status__in=["pending", "confirmed"],
        ).values_list("date", "time_slot")
    )
    context = {
        "booked_slots": booked_slots,
        "time_slots": Appointment.TimeSlot.choices,
        "purposes": Appointment.Purpose.choices,
        "today": datetime.date.today().isoformat(),
    }
    return render(request, "portfolio/process.html", context)


HOBBIES = [
    ("🚴", "Cycling", "Long rides clear my head and build discipline — same muscles as shipping software."),
    ("📚", "Reading", "From system design papers to fiction. Always a book open somewhere."),
    ("🔬", "Researching", "Deep-diving into topics that interest me. Curiosity is my default mode."),
    ("✍️", "Writing", "I write to clarify thinking. Articles, notes, documentation."),
    ("🏊", "Swimming", "Meditative, full-body. Good counterweight to sitting at a desk."),
    ("🥾", "Hiking", "Nairobi's hills and beyond. Nature resets perspective."),
    ("🌿", "Exploring Nature", "Forests, parks, national reserves. Being outdoors keeps me grounded."),
    ("✈️", "Travelling", "New places, new ways people solve problems. Invaluable for a builder."),
]


VALUE_PROPS = [
    ("layers", "Architecture that lasts", "I design systems for the long term: clear data models, documented decisions, and code your future team can maintain."),
    ("zap", "Shipping velocity", "I work iteratively with weekly demos. You see real, working software — not slide decks. No surprises at the end."),
    ("shield-check", "Production-grade quality", "Tests, CI/CD, Docker, monitoring. I treat every project like it has thousands of users — because yours might."),
    ("message-square", "Clear communication", "Weekly written updates, async-first, honest estimates. I flag problems early, not at the deadline."),
    ("code-2", "Backend depth, full-stack range", "Deep Python/Django expertise with a fluent frontend range across React, Vue, TypeScript, and Java."),
    ("users", "Collaborative by default", "I work with your team, not around it. Code reviews, documentation, knowledge transfer — part of every engagement."),
]


def work_with_me(request):
    return render(request, "portfolio/work_with_me.html", {
        "value_props": VALUE_PROPS,
    })


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("message", "").strip()

        if name and email and subject and body:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=body)
            messages.success(request, "Message sent! I'll get back to you within 24 hours.")
        else:
            messages.error(request, "Please fill in all fields.")

    return redirect("work_with_me")


def resume(request):
    from .models import WorkExperience
    try:
        config = SiteConfig.objects.get(pk=1)
    except SiteConfig.DoesNotExist:
        config = None
    return render(request, "portfolio/resume.html", {
        "site_config": config,
        "experiences": WorkExperience.objects.order_by("-start_date"),
        "projects": Project.objects.filter(featured=True).order_by("order")[:5],
    })


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
            return redirect("process")

        if not all([name, email, time_slot]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("process")

        if Appointment.objects.filter(date=date, time_slot=time_slot,
                                      status__in=["pending", "confirmed"]).exists():
            messages.error(request, "That slot is already taken — please pick another time.")
            return redirect("process")

        Appointment.objects.create(
            name=name, email=email, date=date,
            time_slot=time_slot, purpose=purpose, message=note,
        )
        messages.success(request,
                         f"Booking request sent for {date.strftime('%B %d')} at "
                         f"{dict(Appointment.TimeSlot.choices)[time_slot]}. "
                         "I'll confirm by email.")

    return redirect("process")
