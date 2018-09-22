from django import template

register = template.Library()


@register
def replace(value, instead_before, instead_after):
    return value.replace(instead_before, instead_after)
