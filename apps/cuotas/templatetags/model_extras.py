from django import template
register = template.Library()

@register.filter
def model_name(obj):
    return obj._meta.model_name
