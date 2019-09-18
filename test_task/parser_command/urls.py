from django.urls import path

from parser_command import views

urlpatterns = [
    path("", views.index, name="home"),
    path("export", views.export, name="export"),
]
