from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id','assigned_driver','driver_number','origin','destination','departure_date','departure_time','cargo_type','hos_cycle','distance','status','created_at')