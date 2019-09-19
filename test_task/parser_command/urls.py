from django.urls import path

from parser_command.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("export", IndexView.export, name="export"),
]
