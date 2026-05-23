from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authentication import BasicAuthentication


schema_view = get_schema_view(
    openapi.Info(
        title="Документация",
        default_version="v1",
    ),
    public=True,
    authentication_classes=[BasicAuthentication],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="web-schema-swagger-ui",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
