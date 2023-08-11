import datetime

from django.forms import Form, ChoiceField, IntegerField, DateTimeField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .structure import TIME_RANGE_DAYS


class ShowLogsForm(Form):
    """
    Search logs form by table, date range and limit for lines
    """

    table = ChoiceField(
        label=_("Table"),
    )
    start_datetime = DateTimeField(
        label=_("First time"),
    )
    end_datetime = DateTimeField(
        initial=timezone.now,
        label=_("last time"),
    )
    limit = IntegerField(
        label=_("Lines limit"),
        initial=100,
    )

    def set_initial(self):
        """
        Set initial value for start_datetime one day earlier.
        """
        if not self.fields["start_datetime"].initial:
            self.fields["start_datetime"].initial = timezone.now() - datetime.timedelta(
                days=TIME_RANGE_DAYS
            )

    def set_table_choices(self, table_list):
        """
        Prepare table choices structure for select field
        """
        self.fields["table"].choices = zip(table_list, table_list)
