"""
Developer notes to avoid future pitfalls.
"""

from datetime import datetime

from libs.dateutil.relativedelta import relativedelta

def age_range_incorrect():
    """
    The below is the incorrect way to implement an age range.
    This implementation leaves out an entire year in between 
    two date ranges!
    
    e.g.
    
        <20, 20-29, 30-39, 40-49, >50
    """
    age_ranges = [(0, -19), (-20,-29), (-30, -39), 
                    (-40, -49), (-50, -200)]
    now = datetime.now()
    print "Start dob\t\t\tEnd dob"
    for (start_age, end_age) in age_ranges:
        start_dob = now + relativedelta(years=end_age)
        end_dob = now + relativedelta(years=start_age)
        print str(start_dob) + "\t" +  str(end_dob)


def age_range_correct():
    """
    The below is the correct way to implement an age range.
    This implementation does not leave out even a second in 
    between two date ranges.
    
    e.g.
    
        <20, 20-29, 30-39, 40-49, >50
    """
    age_ranges = [(0, -20), (-20,-30), (-30, -40), 
                    (-40, -50), (-50, -200)]
    now = datetime.now()
    print "Start dob\t\t\tEnd dob"
    for (start_age, end_age) in age_ranges:
        start_dob = now + relativedelta(years=end_age)
        start_dob = start_dob.replace(hour=0, minute=0, second=0)
        end_dob = now + relativedelta(years=start_age)
        end_dob = end_dob + relativedelta(days=-1)
        end_dob = end_dob.replace(hour=23, minute=59, second=59)
        print str(start_dob) + "\t" +  str(end_dob)





