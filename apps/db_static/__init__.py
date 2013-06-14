# Initialize the categories database if not exist
from apps.db_static.models import Category
from django.db import IntegrityError

if Category.objects.count() < 5:
    with open("docs/categories.txt", "r") as fid:
        for cat in fid.readlines():
            clean = cat.strip().replace(")", "")
            name, alias = clean.split(" (")
            try:
                Category.objects.create(name=name, alias=alias)
            except IntegrityError:
                continue 
