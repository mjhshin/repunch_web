from parse.utils import cloud_call
import sys


def register_employee(first_name, last_name, username=None, 
        password=None, email=None, retailer_pin=None):
        
        if username is None: 
            username = first_name
        if password is None: 
            password = first_name
        if email is None: 
            email = first_name + "@" + last_name + ".com"
        if retailer_pin is None: 
            retailer_pin = "MQZLBL"
            
        print cloud_call("register_employee", {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "email": email,
            "retailer_pin": retailer_pin,
        })
        
        
first_name, last_name, username, password, email, retailer_pin =\
    None, None, None, None, None, None
        
try:
    first_name = str(sys.argv[1])
    last_name = str(sys.argv[2])
    username = str(sys.argv[3])
    if username == "0":
        username = None
    password = str(sys.argv[4])
    if password == "0":
        password = None
    email = str(sys.argv[5])
    if email == "0":
        email = None
    retailer_pin = str(sys.argv[6])
    if retailer_pin == "0":
        retailer_pin = None
except Exception:
    pass
    
register_employee(first_name, last_name, username, password, email, retailer_pin)
