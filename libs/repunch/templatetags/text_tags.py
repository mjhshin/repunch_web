from django import template

register = template.Library()

@register.filter
def trim_to_dots(string, x):
    """
    Returns the first x chars of the string and truncates the rest.
    Appends 3 dots at the end.

    e.g. "hello world|trim_to_dots:5 returns "hello..."
    """
    if string is None:
        return "null"
    if len(string) > x:
        return string[:x] + "..."
    else:
        return string
