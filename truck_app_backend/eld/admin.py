from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(ELDDailyLog)
class ELDDailyLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip_id', 'day_number', 'driving_hours', 'on_duty_hours', 'off_duty_hours')
