from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

admin.site.site_title = f"Integrador AVA (v{settings.APP_VERSION})"
admin.site.site_header = admin.site.site_title

urlpatterns = [
    path(
        f"{settings.ROOT_URL_PATH}/",
        include(
            [
                path("admin/login/", RedirectView.as_view(url="/api/login/")),
                path("admin/logout/", RedirectView.as_view(url="/api/logout/")),
                path("admin/", admin.site.urls),
                path("", include("health.urls")),
                path("", include("security.urls")),
                path("", include("integrador.urls")),
            ]
        ),
    ),
    path("", RedirectView.as_view(url=settings.ROOT_URL_PATH)),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns.append(path(f"{settings.ROOT_URL_PATH}/__debug__/", include(debug_toolbar.urls)))
else:
    urlpatterns += [
        re_path(f"{settings.STATIC_URL}/media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
        re_path(f"{settings.STATIC_URL}/static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    ]
