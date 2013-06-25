from django.http import HttpResponse
from django.shortcuts import render
import json

from parse.auth.decorators import login_required
from parse import session as SESSION

@login_required
def index(request):
    data = {"workbench_nav":True,
        "redemptions":SESSION.get_redemptions(request.session)}
    return render(request, 'manage/workbench.djhtml', data)
