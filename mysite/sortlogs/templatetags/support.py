from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def get_row_header(row: list, number: int) -> str:
    return row[number]


@register.simple_tag
def add_empty_td(row: list, headers: list) -> str:
    number_of_td = len(headers) - len(row)
    if 0 < number_of_td:
        return mark_safe("<td>&nbsp;</td>" * number_of_td)
    return ""
