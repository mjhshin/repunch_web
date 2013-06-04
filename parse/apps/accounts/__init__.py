"""
DEFAULT_ACC_SETTINGS = {
    'punches_customer':1,
    'punches_employee':50,
    'punches_facebook':20,
}
"""

# Value must be the same as parse.apps.accounts.models constants
# cannot import it here since it will cause cyclic imports
ACTIVE = 'Active'
INACTIVE = 'Inactive'

FREE = "FREE"
MIDDLEWEIGHT = "MIDDLEWEIGHT"
HEAVYWEIGHT = "HEAVYWEIGHT"

UNLIMITED = -1
ERROR = "Billing Error"

# FREE
free_type = {"name":FREE,
                "monthly_cost":0, "max_users":50,
                "max_messages":1, "level":0, 
                "status": ACTIVE }

# MIDDLE
middle_type = {"name":MIDDLEWEIGHT, 
                "monthly_cost":39, "max_users":150,
                "max_messages":4, "level":1, 
                "status": ACTIVE }

# HEAVY
heavy_type = {"name":HEAVYWEIGHT, 
                "monthly_cost":59, "max_users":UNLIMITED,
                "max_messages":8, "level":2, 
                "status": ACTIVE }

sub_type = {
    0:free_type,
    1:middle_type,
    2:heavy_type,
}
    




