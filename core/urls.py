from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "core"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("", login_required(views.LandingView.as_view()), name="landing"),
    path(
        "stages/<int:pk>/",
        login_required(views.StageDetailView.as_view()),
        name="stage_detail",
    ),
]


