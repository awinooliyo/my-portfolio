from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("projects/", views.projects_list, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),

    path("writing/", views.writing_list, name="writing"),
    path("writing/<slug:slug>/", views.writing_detail, name="writing_detail"),

    path("library/", views.library, name="library"),

    path("process/", views.process, name="process"),

    path("work-with-me/", views.work_with_me, name="work_with_me"),

    path("resume/", views.resume, name="resume"),
    path("contact/", views.contact, name="contact"),
    path("book/", views.book_appointment, name="book_appointment"),

    # legacy redirects
    path("blog/", views.writing_list, name="blog_list"),
    path("blog/<slug:slug>/", views.writing_detail, name="blog_detail"),
]
