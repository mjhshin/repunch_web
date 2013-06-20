from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import HttpResponse
from datetime import timedelta, datetime
import json

from parse.apps.patrons.models import Patron
from parse import session as SESSION
from parse.session import get_time_now
from parse.core.advanced_queries import relational_query
from parse.auth.decorators import login_required
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta

@login_required
def index(request):
    data = {'analysis_nav': True}
    data['rewards'] =\
            SESSION.get_store(request.session).get("rewards")
    return render(request, 'manage/analysis.djhtml', data)

@login_required
def trends_graph(request, data_type=None, start=None, end=None ):
    store = SESSION.get_store(request.session)
    
    start = datetime.strptime(start, "%Y-%m-%d")
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.strptime(end, "%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    columns = []
    rows = []
    
    if data_type == 'punches':
        columns = [
                    {"id":"", "label":"Date", "type":"string"},
                    {"id":"", "label":'Punches', "type":"number"}
                   ]
            
        punch_map = {}
        punches = store.get('punches', createdAt__lte=end,
                    createdAt__gte=start,order='createdAt')
        
        #create dictionary for easy search
        if punches:
            for punch in punches:
                key = punch.createdAt.strftime("%m/%d")
                if key in punch_map:
                    punch_map[key] = punch_map[key]+\
                                        punch.get('punches')
                else:
                    punch_map[key] = punch.get('punches')
    
        rows = []
        for single_date in rputils.daterange(start, end):
            str_date = single_date.strftime("%m/%d")
            c = [{"v": str_date}]
            try:
                punch_count = punch_map[str_date]
            except KeyError:
                punch_count = 0
                    
            c.append({"v": punch_count})
            rows.append({'c': c})
    elif data_type == 'facebook':
        columns = [
                    {"id":"", "label":"Date", "type":"string"},
                    {"id":"", "label":'Posts', "type":"number"}
                   ]
            
        post_map = {}
        posts = store.get("facebookPosts", createdAt__lte=end,
                    createdAt__gte=start)
        #create dictionary for easy search
        if posts:
            for post in posts:
                key = post.createdAt.strftime("%m/%d")
                if key in post_map:
                    post_map[key] = post_map[key] + 1
                else:
                    post_map[key] = 1
    
        rows = []
        for single_date in rputils.daterange(start, end):
            str_date = single_date.strftime("%m/%d")
            c = [{"v": str_date}]
            try:
                post_count = post_map[str_date]
            except KeyError:
                post_count = 0
                    
            c.append({"v": post_count})
            rows.append({'c': c})
    else: #patrons
        # total number of patrons at a particular date
        columns = [
                    {"id":"", "label":"Date", "type":"string"},
                    {"id":"", "label":'Patrons', "type":"number"}
                   ]
        rows = []
        for single_date in rputils.daterange(start, end):
            str_date = single_date.strftime("%m/%d")
            # need to set single_date's hours, mins, sec to max
            d = single_date.replace(hour=23, minute=59, second=59)
            c = [{"v": str_date}]
            patron_count = store.get('patronStores', count=1,
                                limit=0, createdAt__lte=d)
                    
            c.append({"v": patron_count})
            rows.append({'c': c})
        
    return HttpResponse(json.dumps({'cols': columns, 'rows': rows}), content_type="application/json")



@login_required
def breakdown_graph(request, data_type=None, filter=None, range=None):
    store = SESSION.get_store(request.session)
    (start, end) = rputils.calculate_daterange(range)
    
    results = [] 
    if data_type == 'punches':
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            
            # WARNING! max punches returned is 1000!
            unknown, male, female = 0, 0, 0 
            male_punches = relational_query(store.objectId, "Store",
                "Punches", "Punch", "Patron", "Patron", 
                {"gender": "male"}, {'createdAt__lte':end,
                    'createdAt__gte':start})['results']
            female_punches = relational_query(store.objectId, "Store",
                "Punches", "Punch", "Patron", "Patron", 
                {"gender": "female"}, {'createdAt__lte':end,
                    'createdAt__gte':start})['results']
            # aggregate the punches
            for p in male_punches:
                male += p.get('punches')
            for p in female_punches:
                female += p.get('punches')

            rows = [start.strftime("%m/%d/%Y")+\
                    ' - '+end.strftime("%m/%d/%Y"),
                    unknown, male, female]
            results.append(rows)
        
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
           
            now = get_time_now(request.session)
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0, 0, 0]
            age_ranges = [(1, 0, -20), (2, -20,-30), (3, -30, -40), (4, -40, -50), (5, -50, -200)]
            for (idx, start_age, end_age) in age_ranges:
                start_dob = now + relativedelta(years=end_age)
                start_dob = start_dob.replace(hour=0, minute=0, 
                                            second=0)
                end_dob = now + relativedelta(years=start_age)
                end_dob = end_dob + relativedelta(days=-1)
                end_dob = end_dob.replace(hour=23, minute=59, 
                                        second=59)
                punches = relational_query(store.objectId, "Store",
                    "Punches", "Punch", "Patron", "Patron", 
                    {'date_of_birth__lte':end_dob,
                     'date_of_birth__gte':start_dob},
                    {'createdAt__lte':end, 
                     'createdAt__gte':start})['results']
                punch_count = 0
                if punches: 
                    for punch in punches:
                        punch_count += punch['punches']
                rows[idx] = punch_count
            results.append(rows)
            
    elif data_type == 'facebook':
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            results.append([
                start.strftime("%m/%d/%Y")+\
                    ' - '+end.strftime("%m/%d/%Y"),
                    0, 
                    relational_query(store.objectId, "Store",
                        "FacebookPosts", "FacebookPost", 
                        "Patron", "Patron", 
                        {"gender": "male"}, {'createdAt__lte':end,
                        'createdAt__gte':start}, count=True), 
                    relational_query(store.objectId, "Store",
                        "FacebookPosts", "FacebookPost", 
                        "Patron", "Patron", 
                        {"gender": "female"}, {'createdAt__lte':end,
                        'createdAt__gte':start}, count=True), 
            ])
        
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
           
            now = get_time_now(request.session)
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0, 0, 0]
            age_ranges = [(1, 0, -20), (2, -20,-29), (3, -30, -39), (4, -40, -49), (5, -50, -200)]
            for (idx, start_age, end_age) in age_ranges:
                start_dob = now + relativedelta(years=end_age)
                start_dob = start_dob.replace(hour=0, minute=0, 
                                            second=0)
                end_dob = now + relativedelta(years=start_age)
                end_dob = end_dob + relativedelta(days=-1)
                end_dob = end_dob.replace(hour=23, minute=59, 
                                        second=59)
                rows[idx] = relational_query(store.objectId, "Store",
                    "FacebookPosts", "FacebookPost", 
                    "Patron", "Patron", 
                    {'date_of_birth__lte':end_dob,
                     'date_of_birth__gte':start_dob},
                    {'createdAt__lte':end, 
                     'createdAt__gte':start}, count=True)
                    
            results.append(rows)
            
    else: # patrons
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            results.append([
                start.strftime("%m/%d/%Y")+\
                    ' - '+end.strftime("%m/%d/%Y"),
                    0, 
                    relational_query(store.objectId, "Store",
                        "PatronStores", "PatronStore", 
                        "Patron", "Patron", 
                        {"gender": "male"}, {'createdAt__lte':end,
                        'createdAt__gte':start}, count=True), 
                    relational_query(store.objectId, "Store",
                        "PatronStores", "PatronStore", 
                        "Patron", "Patron", 
                        {"gender": "female"}, {'createdAt__lte':end,
                        'createdAt__gte':start}, count=True), 
            ])
            
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
            
            now = get_time_now(request.session)
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0, 0, 0]
            age_ranges = [(1, 0, -20), (2, -20,-30), (3, -30, -39), (4, -40, -50), (5, -50, -200)]
            for (idx, start_age, end_age) in age_ranges:
                start_dob = now + relativedelta(years=end_age)
                start_dob = start_dob.replace(hour=0, minute=0, 
                                            second=0)
                end_dob = now + relativedelta(years=start_age)
                end_dob = end_dob + relativedelta(days=-1)
                end_dob = end_dob.replace(hour=23, minute=59, 
                                        second=59)
                rows[idx] = relational_query(store.objectId, "Store",
                    "PatronStores", "PatronStore", 
                    "Patron", "Patron", 
                    {'date_of_birth__lte':end_dob,
                     'date_of_birth__gte':start_dob},
                    {'createdAt__lte':end, 
                     'createdAt__gte':start}, count=True)
            results.append(rows)
        
    return HttpResponse(json.dumps(results), content_type="application/json")
