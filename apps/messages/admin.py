from django.contrib import admin
from apps.messages.models import Message, Feedback

admin.site.register(Message)
admin.site.register(Feedback)