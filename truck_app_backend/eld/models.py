from django.db import models

class ELDDailyLog(models.Model):

    trip_id = models.IntegerField()

    day_number = models.IntegerField()

    driving_hours = models.FloatField()
    on_duty_hours = models.FloatField()
    off_duty_hours = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)