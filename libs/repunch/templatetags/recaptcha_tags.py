from django import template

from libs import recaptcha
from repunch.settings import RECAPTCHA_TOKEN, RECAPTCHA_ATTEMPTS

register = template.Library()

@register.filter
def display_recaptcha(session):
    """ returns true if recaptcha should be displayed """
    return RECAPTCHA_TOKEN in session and session[\
            RECAPTCHA_TOKEN] >= RECAPTCHA_ATTEMPTS
    
    
@register.filter
def get_recaptcha(x):
    """ calls recaptcha displayhtml """
    return recaptcha.displayhtml()
