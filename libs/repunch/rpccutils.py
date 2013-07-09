#file use for helper functions for the repunch class
import re
from datetime import timedelta 

# Regex for valid card numbers
CC_ACCEPTED = {
    'mastercard':'^5[1-5][0-9]{14}$',
    'visa':'^4[0-9]{12}(?:[0-9]{3})?$',
    'amex':'^3[47][0-9]{13}$',
    'discover':'^6(?:011|5[0-9]{2})[0-9]{12}$',
}

def validate_checksum(number_as_string):
    """ checks to make sure that the card passes a luhn mod-10 checksum """
    ccsum = 0
    num_digits = len(number_as_string)
    oddeven = num_digits & 1

    for i in range(0, num_digits):
        digit = int(number_as_string[i])

        if not (( i & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        ccsum = ccsum + digit
        
    return ( (ccsum % 10) == 0 )

def validate_cc_type(number):
    """ Checks to make sure that the Digits match the CC pattern """
    
    for _,regex in CC_ACCEPTED.iteritems():
        if re.compile(regex).match(number) != None:
            return True
    
    return False

def get_cc_type(number):
    """ Checks to make sure that the Digits match the CC pattern """
    
    for name,regex in CC_ACCEPTED.iteritems():
        if re.compile(regex).match(number) != None:
            return name 
    
    return None