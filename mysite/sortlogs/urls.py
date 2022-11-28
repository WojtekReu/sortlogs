"""
Remember to restrict url for staff members
"""
from django.urls import path

from .views import ShowDateLogs, ShowLogs, GraphLogs
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    path('show-date-logs/', staff_member_required(ShowDateLogs.as_view()), name='show_date_logs'),
    path('show-logs/', staff_member_required(ShowLogs.as_view()), name='show_logs'),
    path('graph-logs/', staff_member_required(GraphLogs.as_view()), name='graph_logs'),
]
