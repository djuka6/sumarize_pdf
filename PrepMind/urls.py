from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    content_view,
    get_all_responses,
    check_view,
)  # Make sure to import your view

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("swagger/", schema_view.with_ui("swagger")),
    path("content/", content_view, name="content"),
    path("responses", get_all_responses, name="get_all_responses"),
    path("check/", check_view, name="check"),
]
