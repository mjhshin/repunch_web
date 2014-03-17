"""
Views for the analysis tab.
"""

from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta, datetime
import json

from parse.utils import make_aware_to_utc
from parse.apps.patrons.models import Patron
from parse import session as SESSION
from parse.decorators import access_required
from parse.core.advanced_queries import relational_query
from parse.auth.decorators import login_required, dev_login_required
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta

@dev_login_required
@login_required
@access_required
def index(request):
    """
    Render the analysis page.
    """
    # sort the rewards by redemption count in descending order
    rewards = SESSION.get_store(request.session).get("rewards")
    rewards.sort(key=lambda k: k['redemption_count'], reverse=True)
            
    return render(request, 'manage/analysis.djhtml', {
        'analysis_nav': True,
        'rewards': rewards,
    })

@dev_login_required
@login_required
@access_required(http_response={"error": "Access denied"})
def trends_graph(request, data_type=None, start=None, end=None ):
    """
    Handles requests for the trends graph.
    """
    store = SESSION.get_store(request.session)
    
    # We need the store's timezone to convert everything to UTC
    # because the time we get from start and end are local times
    # and in order to convert to UTC we must first make start and end
    # timezone aware. We use parse.utils.make_aware_to_utc to do
    # this in 1 step. We convert everything to UTC for use in queries.
    store_timezone = SESSION.get_store_timezone(request.session)
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    start_aware = make_aware_to_utc(start, store_timezone)
    end_aware = make_aware_to_utc(end, store_timezone)
    
    rows, columns = [], []
    
    if data_type == 'punches':
        # we need to return graph data for punches for all days in
        # between start and end.
        
        # columns contains the data that any given row needs to have.
        # rows contains multiple dates paired with punch count
        columns = [
            {"id":"", "label":"Date", "type":"string"},
            {"id":"", "label":'Punches', "type":"number"}
        ]
            
        # get the Punches
        punches = store.get('punches', createdAt__lte=end_aware,
            createdAt__gte=start_aware,order='createdAt', limit=900)
            
        # have to clear the punches cache attr of store filled
        # by the above query
        store.punches = None
        
        #create dictionary for easy search
        punch_map = {}
        if punches:
            for punch in punches:
                # The keys in the punch map is the month/day of the
                # createdAt of the punch object. We also convert it
                # to the store's local time for when we send back the
                # data to the client.
                key = timezone.localtime(punch.createdAt, 
                    store_timezone).strftime("%m/%d")
                    
                if key in punch_map:
                    # add to the punch count for the existing key
                    punch_map[key] =\
                        punch_map[key] + punch.get('punches')
                        
                else:
                    # initialize the key in the punch map
                    punch_map[key] = punch.get('punches')
    
        for single_date in rputils.daterange(start, end):
            # we now populate the rows with the corresponding punch counts
            # str_date is a day in between start and end with the
            # same format as a key in our punch_map            
            str_date = single_date.strftime("%m/%d")
            
            try:
                punch_count = punch_map[str_date]
            except KeyError:
                punch_count = 0
                    
            # the first item in our row is the date
            # the second item is the corresponding punch_count
            row = [{"v": str_date}, {"v": punch_count}]
            rows.append({'c': row})
            
    elif data_type == 'facebook':
        # we need to return graph data for facebook posts for
        # all days in between start and end.
        
        # columns contains the data that any given row needs to have.
        # rows contains multiple dates paired with post count
        columns = [
            {"id":"", "label":"Date", "type":"string"},
            {"id":"", "label":'Posts', "type":"number"}
        ]
            
        # get the FacebookPosts
        posts = store.get("facebookPosts", createdAt__lte=end,
                    createdAt__gte=start, limit=900)
        # have to clear the facebookPosts cache attr of store filled
        # by the above query
        store.facebookPosts = None
        
        #create dictionary for easy search
        post_map = {}
        if posts:
            for post in posts:
                # The keys in the post map is the month/day of the
                # createdAt of the punch object. We also convert it
                # to the store's local time for when we send back the
                # data to the client.
                key = timezone.localtime(post.createdAt, 
                    store_timezone).strftime("%m/%d")
                    
                if key in post_map:
                    # add to the post count for the existing key
                    post_map[key] = post_map[key] + 1
                    
                else:
                    # initialize the post count
                    post_map[key] = 1
    
        for single_date in rputils.daterange(start, end):
            # we now populate the rows with the corresponding post counts
            # str_date is a day in between start and end with the
            # same format as a key in our punch_map    
            str_date = single_date.strftime("%m/%d")
            
            try:
                post_count = post_map[str_date]
            except KeyError:
                post_count = 0
                    
            # the first item in our row is the date
            # the second item is the corresponding post_count
            row = [{"v": str_date}, {"v": post_count}]
            rows.append({'c': row})
            
    else: 
        # we need to return graph data for unique patrons for
        # all days in between start and end.
        
        # columns contains the data that any given row needs to have.
        # rows contains multiple dates paired with accumulative patron count
        columns = [
            {"id":"", "label":"Date", "type":"string"},
            {"id":"", "label":'Patrons', "type":"number"}
        ]

        for single_date in rputils.daterange(start, end):
            # str_date is a day in between start and end with the
            # same format as a key in our punch_map    
            str_date = single_date.strftime("%m/%d")
            
            # FIXME In order to get the cumulative count for each day,
            # we make a query of the count for each day. Optimization?
            d = single_date.replace(hour=23, minute=59, second=59)
            d_aware = make_aware_to_utc(d, store_timezone)
            patron_count = store.get('patronStores', count=1,
                                limit=0, createdAt__lte=d_aware)
                    
            row = [{"v": str_date}, {"v": patron_count}]
            rows.append({'c': row})
        
    # return the graph data
    return HttpResponse(json.dumps({'cols': columns, 'rows': rows}),
        content_type="application/json")

@dev_login_required
@login_required
@access_required(http_response={"error": "Access denied"})
def breakdown_graph(request, data_type=None, filter=None, range=None):
    """
    handles requests for the breakdown graph.
    """
    store = SESSION.get_store(request.session)
    store_timezone = SESSION.get_store_timezone(request.session)
    (start, end) = rputils.calculate_daterange(range)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    # need to make aware and then convert to utc for querying
    start_aware = make_aware_to_utc(start, store_timezone)
    end_aware = make_aware_to_utc(end, store_timezone)
    
    results = [] 
    if data_type == 'punches':
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            
            # WARNING! max punches returned is 1000!
            unknown, male, female = 0, 0, 0 
            male_punches = relational_query(store.objectId, "Store",
                "Punches", "Punch", "Patron", "Patron", 
                {"gender": "male"}, {'createdAt__lte':end_aware,
                    'createdAt__gte':start_aware})
            female_punches = relational_query(store.objectId, "Store",
                "Punches", "Punch", "Patron", "Patron", 
                {"gender": "female"}, {'createdAt__lte':end_aware,
                    'createdAt__gte':start_aware})
                    
            if male_punches:
                male_punches = male_punches['results']
                # aggregate the punches
                for p in male_punches:
                    male += p.get('punches')
            
            if female_punches:
                female_punches = female_punches['results']
                for p in female_punches:
                    female += p.get('punches')

            rows = [start.strftime("%m/%d/%Y")+\
                    ' - '+end.strftime("%m/%d/%Y"),
                    unknown, male, female]
            results.append(rows)
        
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
           
            now = datetime.now()
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
                
                # need to make aware and then convert to utc for querying
                start_dob_aware = make_aware_to_utc(start_dob, store_timezone)
                end_dob_aware = make_aware_to_utc(end_dob, store_timezone)
                
                punches = relational_query(store.objectId, "Store",
                    "Punches", "Punch", "Patron", "Patron", 
                    {'date_of_birth__lte':end_dob_aware,
                     'date_of_birth__gte':start_dob_aware},
                    {'createdAt__lte':end_aware, 
                     'createdAt__gte':start_aware})
                punch_count = 0
                if punches: 
                    punches = punches['results']
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
                        {"gender": "male"}, {'createdAt__lte':end_aware,
                        'createdAt__gte':start_aware}, count=True), 
                    relational_query(store.objectId, "Store",
                        "FacebookPosts", "FacebookPost", 
                        "Patron", "Patron", 
                        {"gender": "female"}, {'createdAt__lte':end_aware,
                        'createdAt__gte':start_aware}, count=True), 
            ])
        
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
           
            now = datetime.now()
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
                                        
                # need to make aware and then convert to utc for querying
                start_dob_aware = make_aware_to_utc(start_dob, store_timezone)
                end_dob_aware = make_aware_to_utc(end_dob, store_timezone)
                
                rows[idx] = relational_query(store.objectId, "Store",
                    "FacebookPosts", "FacebookPost", 
                    "Patron", "Patron", 
                    {'date_of_birth__lte':end_dob_aware,
                     'date_of_birth__gte':start_dob_aware},
                    {'createdAt__lte':end_aware, 
                     'createdAt__gte':start_aware}, count=True)
                    
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
                        {"gender": "male"}, {'createdAt__lte':end_aware,
                        'createdAt__gte':start_aware}, count=True), 
                    relational_query(store.objectId, "Store",
                        "PatronStores", "PatronStore", 
                        "Patron", "Patron", 
                        {"gender": "female"}, {'createdAt__lte':end_aware,
                        'createdAt__gte':start_aware}, count=True), 
            ])
            
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
            
            now = datetime.now()
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
                                        
                # need to make aware and then convert to utc for querying
                start_dob_aware = make_aware_to_utc(start_dob, store_timezone)
                end_dob_aware = make_aware_to_utc(end_dob, store_timezone)
                
                rows[idx] = relational_query(store.objectId, "Store",
                    "PatronStores", "PatronStore", 
                    "Patron", "Patron", 
                    {'date_of_birth__lte':end_dob_aware,
                     'date_of_birth__gte':start_dob_aware},
                    {'createdAt__lte':end_aware, 
                     'createdAt__gte':start_aware}, count=True)
            results.append(rows)
        
    return HttpResponse(json.dumps(results), content_type="application/json")
