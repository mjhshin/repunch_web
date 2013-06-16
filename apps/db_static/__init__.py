# Initialize the categories database if not exist
from apps.db_static.models import Category
from django.db import IntegrityError
from repunch.settings import FS_SITE_DIR

if Category.objects.count() < 1:
    # ec2 machine python does not start at repunch_web
    cats = []
    try:
        with open("docs/categories.txt", "r") as fid:
            cats = fid.readlines()
    except IOError:
        with open(FS_SITE_DIR + "docs/categories.txt", "r") as fid:
            cats = fid.readlines()
    
    for cat in cats:
        clean = cat.strip().replace(")", "")
        name, alias = clean.split(" (")
        try:
            Category.objects.create(name=name, alias=alias)
        except IntegrityError:
            continue 
