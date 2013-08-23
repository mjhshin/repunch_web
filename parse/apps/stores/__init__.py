
# payment types
MONTHLY = "monthly"
SMARTPHONE = "smartphone"

# Access levels per account basis
ACCESS_ADMIN = "faa" # full admin access
ACCESS_PUNCHREDEEM = "apr" # allow punch redeem
ACCESS_NONE = "na" # no access

def format_phone_number(num_str):
    """
    Takes in a string 7187371994 and outputs (718) 737-1994.
    """
    return "("+num_str[:3]+") "+num_str[3:6]+"-"+num_str[6:10]
