from django.db import models 


class LogBoss(models.Model):
    is_running = models.BooleanField()
