from django.db import models
from user.models import User
# Create your models here.

class Trip(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    HOS_CHOICES = [
        ('70/8', '70 Hours / 8 Days'),
        ('60/7', '60 Hours / 7 Days'),
    ]
    CARGO_TYPE_CHOICES = [
        ('general', 'General'),
        ('refrigerated', 'Refrigerated'),
        ('oversized', 'Oversized'),
        ('livestock', 'Livestock'),
        ('hazmat', 'Hazmat'),
    ]
    assigned_driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_trips',
        null=True
    )
    co_driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='co_driver_trips',
        null=True,
        blank=True
    )
    driver_number = models.CharField(max_length=100)
    tractor_number = models.CharField(max_length=100)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    cargo_type = models.CharField(
        max_length=50,
        choices=CARGO_TYPE_CHOICES
    )
    shipper_name = models.CharField(max_length=255)
    load_number = models.CharField(max_length=100)
    hos_cycle = models.CharField(
        max_length=10,
        choices=HOS_CHOICES,
        default='70/8',
        null=False,
        blank=False
    )
    current_cycle_used = models.FloatField(default=0)
    distance = models.FloatField(
        null=True,
        blank=True
    )
    duration = models.FloatField(
        null=True,
        blank=True
    )
    route_geometry = models.JSONField(null=True, blank=True)
    route_instructions = models.JSONField(
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origin} → {self.destination}"