from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone


class Status(models.TextChoices):
    PENDING = 'pending'
    COMPLETE = 'complete'
    CANCELED = 'canceled'


class OrderManager(models.Manager):
    def canceled(self):
        return self.filter(latest_status=Status.CANCELED)

    def pending(self):
        return self.filter(latest_status=Status.PENDING)

    def complete(self):
        return self.filter(latest_status=Status.COMPLETE)


class Order(models.Model):
    objects = OrderManager()

    latest_status = models.CharField(max_length=10, choices=Status.choices, default=None, null=True, blank=True,
                                     db_index=True)


class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(default=timezone.now)


@receiver([post_delete, post_save], sender=OrderStatus)
def update_order_status(sender, instance, **kwargs):
    print("Updating order status")
    order = instance.order
    last_status = order.orderstatus_set.order_by('-created').first()
    if last_status:
        order.latest_status = last_status.status
    else:
        order.latest_status = instance.status
    order.save()
