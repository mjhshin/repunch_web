from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import HttpResponse
from datetime import timedelta
import datetime, json

from apps.rewards.models import Reward
from apps.employees.models import Employee
from apps.patrons.models import Patron, FacebookPost
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta

@login_required
def index(request):
    data = {'analysis_nav': True}
    account = request.session['account']
    
    
    data['rewards'] = Reward.objects.filter(store=account.store.id).order_by('reward_name')
    return render(request, 'manage/analysis.djhtml', data)



@login_required
def trends_graph(request, data_type=None, start=None, end=None ):
    from apps.rewards.models import Punch
        
    account = request.session['account']
    
    start = datetime.datetime.strptime(start, "%Y-%m-%d")#.strftime("%Y-%m-%d")
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.datetime.strptime(end, "%Y-%m-%d")#.strftime("%Y-%m-%d")
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    columns = []
    rows = []
    
    if data_type == 'punches':
        columns = [
                    {"id":"", "label":"Date", "type":"string"},
                    {"id":"", "label":'Punches', "type":"number"}
                   ]
            
        punch_map = {}
        punches = Punch.objects.extra(select={'myd': "date(date_punched)"}).values('myd').filter(date_punched__range=(start, end),employee__store=account.store).annotate(num_punches=Sum('punches')).order_by('-date_punched')
        
        #create dictionary for easy search
        for punch in punches:
            punch_map[punch['myd'].strftime("%m/%d")] = punch['num_punches'] 
    
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
        posts = FacebookPost.objects.extra(select={'myd': "date(date_posted)"}).values('myd').filter(date_posted__range=(start, end),store=account.store).annotate(num_posts=Count('id'))
        #create dictionary for easy search
        for post in posts:
            post_map[post['myd'].strftime("%m/%d")] = post['num_posts'] 
    
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
        columns = [
                    {"id":"", "label":"Date", "type":"string"},
                    {"id":"", "label":'Patrons', "type":"number"}
                   ]
            
        punch_map = {}
        punches = Punch.objects.extra(select={'myd': "date(date_punched)"}).values('myd').filter(date_punched__range=(start, end),employee__store=account.store).annotate(num_patrons=Count('patron', distinct=True))
        
        #create dictionary for easy search
        for punch in punches:
            punch_map[punch['myd'].strftime("%m/%d")] = punch['num_patrons'] 
    
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
        
    return HttpResponse(json.dumps({'cols': columns, 'rows': rows}), content_type="application/json")



@login_required
def breakdown_graph(request, data_type=None, filter=None, range=None):
    from apps.rewards.models import Punch
    from django.db import connection
    
    account = request.session['account']    
    
    (start, end) = rputils.calculate_daterange(range)
    
    results = [] 
    if data_type == 'punches':
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            
            punches = Punch.objects.values('patron__gender').filter(date_punched__range=[start, end], employee__store=account.store).annotate(num_punches=Sum('punches'))     
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0]
            for punch in punches:
                rows[punch['patron__gender']+1] = punch['num_punches']
            results.append(rows)
        
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
           
            now = datetime.datetime.now()
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0, 0, 0]
            age_ranges = [(1, 0, -19), (2, -20,-29), (3, -30, -39), (4, -40, -49), (5, -50, -200)]
            for (idx, start_age, end_age) in age_ranges:
                start_dob = now + relativedelta(years=end_age)
                end_dob = now + relativedelta(years=start_age)
                val = Punch.objects.values('employee__store').filter(date_punched__range=[start, end], patron__dob__range=[start_dob, end_dob], employee__store=account.store).annotate(num_punches=Sum('punches'))
                if len(val) > 0:
                    rows[idx] = val[0]['num_punches']
            results.append(rows)
            
    elif data_type == 'facebook':
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            
            posts = FacebookPost.objects.values('patron__gender').filter(date_posted__range=[start, end], store=account.store).annotate(num_posts=Count('id'))     
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0]
            for post in posts:
                rows[post['patron__gender']+1] = post['num_posts']
            results.append(rows)
        
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
           
            now = datetime.datetime.now()
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0, 0, 0]
            age_ranges = [(1, 0, -19), (2, -20,-29), (3, -30, -39), (4, -40, -49), (5, -50, -200)]
            for (idx, start_age, end_age) in age_ranges:
                start_dob = now + relativedelta(years=end_age)
                end_dob = now + relativedelta(years=start_age)
                val = FacebookPost.objects.values('store').filter(date_posted__range=[start, end], patron__dob__range=[start_dob, end_dob], store=account.store).annotate(num_posts=Count('id'))
                
                if len(val) > 0:
                    rows[idx] = val[0]['num_posts']
                    
            results.append(rows)
            
    else: #patrons
        if filter == 'gender':
            results.append(["Range", "Unknown", "Male", "Female"]);
            
            punches = Punch.objects.values('patron__gender').filter(date_punched__range=[start, end], employee__store=account.store).annotate(num_patrons=Count('patron', distinct=True))     
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0]
            for punch in punches:
                rows[punch['patron__gender']+1] = punch['num_patrons']
            results.append(rows)
            
        elif filter == 'age':
            results.append(["Range", "<20", "20-29", "30-39", "40-49", ">50"]);
            
            now = datetime.datetime.now()
            rows = [start.strftime("%m/%d/%Y")+' - '+end.strftime("%m/%d/%Y"), 0, 0, 0, 0, 0]
            age_ranges = [(1, 0, -19), (2, -20,-29), (3, -30, -39), (4, -40, -49), (5, -50, -200)]
            for (idx, start_age, end_age) in age_ranges:
                start_dob = now + relativedelta(years=end_age)
                end_dob = now + relativedelta(years=start_age)
                val = Punch.objects.values('employee__store').filter(date_punched__range=[start, end], patron__dob__range=[start_dob, end_dob], employee__store=account.store).annotate(num_patrons=Count('patron', distinct=True))
                if len(val) > 0:
                    rows[idx] = val[0]['num_patrons']
            results.append(rows)
        
    return HttpResponse(json.dumps(results), content_type="application/json")
