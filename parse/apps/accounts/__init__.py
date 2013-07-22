
FREE = "FREE"
MIDDLEWEIGHT = "MIDDLEWEIGHT"
HEAVYWEIGHT = "HEAVYWEIGHT"

UNLIMITED = -1
ERROR = "Billing Error"

# FREE
free_type = {"name":FREE,
                "monthly_cost":0, "max_users":49,
                "max_messages":2, "level":0}

# MIDDLE
middle_type = {"name":MIDDLEWEIGHT, 
                "monthly_cost":39, "max_users":99,
                "max_messages":4, "level":1}

# HEAVY
heavy_type = {"name":HEAVYWEIGHT, 
                "monthly_cost":69, "max_users":UNLIMITED,
                "max_messages":8, "level":2}

sub_type = {
    0:free_type,
    1:middle_type,
    2:heavy_type,
}

