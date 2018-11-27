from django import template

register = template.Library()


def replace(value, instead_before, instead_after):
    return value.replace(instead_before, instead_after)


@register.simple_tag
def str_length(value):
    return len(value)


@register.filter
def split_string(str_split, split_char="|"):
    print(str_split.split("|"))
    return str_split.split(split_char)
