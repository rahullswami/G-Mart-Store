from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Dictionary se value get karne ke liye"""
    return d.get(key, [])