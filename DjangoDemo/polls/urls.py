from django.urls import path

from . import views

urlpatterns = [
    path("", views.DemoView.as_view(), name="demo"),
]
