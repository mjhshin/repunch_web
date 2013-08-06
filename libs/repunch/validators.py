from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

alphanumeric = RegexValidator(regex=r"^[a-zA-Z0-9_ ]+$", 
    message="Must contain only alpha-numeric characters and spaces.",
    code="not_alphanumeric")
                    
numeric = RegexValidator(regex=r"^[0-9]+$", 
    message="Must contain only numbers.", code="non_numeric")
                    
alphanumeric_no_space = RegexValidator(regex=r"^[a-zA-Z0-9_]+$", 
    message="Must contain only alpha-numeric characters " +\
        "without spaces.", code="not_alphanumeric_no_space")
                    
def required(value):
    """
    Django does not strip whitespaces so entering only spaces
    in an input field by-passes the "This field is required." error 
    """
    if len(value.strip()) == 0:
        raise ValidationError(u"This field is required.")
