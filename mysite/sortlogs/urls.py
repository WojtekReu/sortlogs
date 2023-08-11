"""
Remember to restrict url for staff members
"""
from django.urls import path

from .views import SearchLogs, GraphLogs, ShowTables, ShowLoadedFiles
from django.contrib.admin.views.decorators import staff_member_required as staff

urlpatterns = [
    path("show-tables/", staff(ShowTables.as_view()), name="show_tables"),
    path("show-loaded-files/", staff(ShowLoadedFiles.as_view()), name="show_loaded_files"),
    path("graph-logs/", staff(GraphLogs.as_view()), name="graph_logs"),
    path("search-logs/", staff(SearchLogs.as_view()), name="search_logs"),
]
