from django.contrib import admin
from django.urls import path, include

# customize admin index site
admin.site.index_template = "admin/custom_index.html"

urlpatterns = [
    # add sortlogs urls before default admin urls
    path("admin/", include(("sortlogs.urls", "sortlogs"), namespace="sortlogs")),
    path("admin/", admin.site.urls),
]
