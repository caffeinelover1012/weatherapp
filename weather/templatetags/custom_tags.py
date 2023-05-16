from django import template

register = template.Library()

@register.filter
def isoformat(value):
    return value.isoformat()