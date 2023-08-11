from typing import Optional

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ShowLogsForm
from .mongo.logs_load import LogsFromDb
from .graphs import input_structure


class SearchLogs(FormView):
    """
    Show log collection names
    """

    template_name = "sortlogs/search_logs.html"
    form_class = ShowLogsForm
    tables_list: Optional[list] = None
    success_url = reverse_lazy("sortlogs:search_logs")

    def get_form(self, form_class=None):
        """
        form needs list of collections
        """
        form = super().get_form(form_class=form_class)
        self.tables_list = LogsFromDb().get_tables()
        form.set_table_choices(self.tables_list)
        form.set_initial()
        return form

    def form_valid(self, form):
        """
        Render the same form with data bellow form.
        """
        table_name = form.cleaned_data["table"]
        start_datetime = form.cleaned_data["start_datetime"]
        end_datetime = form.cleaned_data["end_datetime"]
        logs_limit = form.cleaned_data["limit"]
        context = {
            "form": form,
            "logs": LogsFromDb().get_logs(table_name, start_datetime, end_datetime, logs_limit),
            "values_list": self.tables_list,
        }
        return render(self.request, self.template_name, context)


class ShowTables(TemplateView):
    """
    Show logs for specified key (day).
    """

    template_name = "sortlogs/show_tables.html"

    def get_context_data(self, **kwargs):
        """
        Get logs list
        """
        context = super().get_context_data(**kwargs)
        context["values_list"] = LogsFromDb().get_tables()
        return context


class ShowLoadedFiles(TemplateView):
    """
    Get loaded files info from LOADED_FILES collection
    """

    template_name = "sortlogs/show_loaded_files.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.table_name = request.GET["table"]
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_name"] = self.request.GET["table"]
        logs_from_db = LogsFromDb()
        if context["table_name"] not in logs_from_db.get_tables():
            context[
                "error_message"
            ] = f"ERROR: Table name '{context['table_name']}' not found in db!"
        else:
            context["values_list"] = LogsFromDb().get_loaded_files(context["table_name"])
        return context


class GraphLogs(TemplateView):
    """
    Show INPUT_FILES structure graph
    """

    template_name = "sortlogs/graph_logs.html"

    def get_context_data(self, **kwargs):
        """
        Create pretty HTML table for structure
        """
        context = super().get_context_data(**kwargs)
        context["table"], context["col_headers"], context["row_headers"] = input_structure()
        return context
