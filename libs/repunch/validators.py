from django.core.validators import RegexValidator

alphanumeric = RegexValidator(r"[\w ]+", "Must contain only alpha-"+\
                    "numeric characters and spaces.")
