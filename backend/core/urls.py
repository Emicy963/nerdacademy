from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/institutions/", include("apps.institutions.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/trainers/", include("apps.trainers.urls")),
    path("api/courses/", include("apps.courses.urls")),
    path("api/classes/", include("apps.classes.urls")),
    path("api/grades/", include("apps.grades.urls")),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
