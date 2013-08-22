from parse.utils import cloud_call
import sys


def register_employee(first_name, last_name,, 
        password=None, email=None, retailer_pin=None):
        
        if password is None: 
            password = first_name
        if email is None: 
            email = first_name + "@" + last_name + ".com"
        if retailer_pin is None: 
            retailer_pin = "MQZLBL"
            
        print cloud_call("register_employee", {
            "first_name": first_name,
            "last_name": last_name,
            "username": email,
            "password": password,
            "email": email,
            "retailer_pin": retailer_pin,
        })
