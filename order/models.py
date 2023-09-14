from django.db import models
from django.utils import timezone


class Order(models.Model):
    pass


class OrderStatus(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        COMPLETE = 'complete'
        CANCELED = 'canceled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(default=timezone.now)
