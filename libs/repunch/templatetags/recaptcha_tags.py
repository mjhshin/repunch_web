from django import template

from libs import recaptcha

register = template.Library()

@register.filter
def display_recaptcha(session):
    """ calls recaptcha displayhtml """
    return recaptcha.displayhtml(session)
