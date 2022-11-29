from django.forms import CharField, Form, ChoiceField
from django.utils.translation import gettext_lazy as _
from .structure import Level, Category, Domain, Port


class ShowDateLogsForm(Form):
    """
    Search log keys according given pattern
    """

    level = ChoiceField(
        choices=Level.gen_list_choices(),
        label=_("Level"),
    )
    category = ChoiceField(
        choices=Category.gen_list_choices(),
        label=_("Category"),
    )
    domain = ChoiceField(
        choices=Domain.gen_list_choices(),
        label=_("Domain"),
    )
    port = ChoiceField(
        choices=Port.gen_list_choices(),
        initial="",
        label=_("Port"),
        required=False,
    )
    date = CharField(
        initial="*",
        label=_("Date"),
        required=False,
    )
