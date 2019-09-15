from django.urls import path
from parserLink import views
# from parserLink.models import dbLog


urlpatterns = [
    path("", views.index, name="home"),
    path("export", views.export, name="export"),
]
