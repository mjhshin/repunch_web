from django import template

from libs import recaptcha

register = template.Library()

@register.filter
def display_recaptcha(x):
    """ calls recaptcha displayhtml """
    return recaptcha.displayhtml()
