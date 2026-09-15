from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("resume/", views.resume, name="resume"),
    path("contact/", views.contact, name="contact"),
    path("book/", views.book_appointment, name="book_appointment"),
]
