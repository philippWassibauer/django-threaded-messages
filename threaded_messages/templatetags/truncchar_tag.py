from django import template

register = template.Library()

@register.filter
# truncate after a certain number of characters
def truncchar(value, arg):
    if len(value) < arg:
        return value
    else:
        return value[:arg] + '...'
