from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

alphanumeric = RegexValidator(r"[\w ]+", "Must contain only alpha-"+\
                    "numeric characters and spaces.")
                    
def required(value):
    """
    Django does not strip whitespaces so entering only spaces
    in an input field by-passes the "This field is required." error 
    """
    if len(value.strip()) == 0:
        raise ValidationError(u"This field is required.")
