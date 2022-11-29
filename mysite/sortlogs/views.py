from typing import Optional

from django.views.generic import FormView, TemplateView

from .forms import ShowDateLogsForm
from .redis.logs_load import LogsFromRedis
from .graphs import input_structure


class ShowDateLogs(FormView):
    """
    Show form and list of keys (all keys are links to logs)
    """

    template_name = "sortlogs/show_date_logs.html"
    form_class = ShowDateLogsForm
    pattern: Optional[str] = None

    def form_valid(self, form: dict):
        """
        Create pattern from form values.
        """
        level = form["level"].value()
        category = form["category"].value()
        domain = form["domain"].value()
        port = form["port"].value()
        date = form["date"].value()
        self.pattern = f"{level}_{category}_{domain}_{port}_{date}"
        # stay on the same page
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs) -> list:
        """
        Get keys from redis for specified pattern.
        """
        context = super().get_context_data(**kwargs)
        if self.pattern is not None:
            context["pattern"] = self.pattern
            lfr = LogsFromRedis()
            keys_list = lfr.get_keys(self.pattern)
            context["keys_list"] = keys_list
            logs_number = {}
            for key in keys_list:
                logs_number[key] = lfr.get_key_logs_number(key)
            context["logs_number"] = logs_number
            # context['keys_list'] = LogsFromRedis().del_all(self.pattern)
        return context


class ShowLogs(TemplateView):
    """
    Show logs for specified key (day).
    """

    template_name = "sortlogs/show_logs.html"

    def get_context_data(self, **kwargs):
        """
        Get logs list
        """
        context = super().get_context_data(**kwargs)
        pattern = self.request.GET.get("pattern")
        if pattern:
            context["pattern"] = pattern
            context["values_list"] = LogsFromRedis().get_values_for_key(pattern)
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
