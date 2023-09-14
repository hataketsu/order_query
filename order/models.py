from django.db import models
from django.utils import timezone


class OrderManager(models.Manager):
    def canceled(self):
        return self.annotate(
            latest_status=models.Subquery(OrderStatus.objects.filter(
                order=models.OuterRef('pk')
            ).order_by('-created').values('status')[:1])
        ).filter(latest_status=OrderStatus.Status.CANCELED)

    def pending(self):
        return self.annotate(
            latest_status=models.Subquery(
                OrderStatus.objects.filter(order=models.OuterRef('pk')).order_by('-created').values('status')[:1]
            )
        ).filter(latest_status=OrderStatus.Status.PENDING)

    def complete(self):
        return self.annotate(
            latest_status=models.Subquery(
                OrderStatus.objects.filter(order=models.OuterRef('pk')).order_by('-created').values('status')[:1]
            )
        ).filter(latest_status=OrderStatus.Status.COMPLETE)


class Order(models.Model):
    pass
    objects = OrderManager()


class OrderStatus(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        COMPLETE = 'complete'
        CANCELED = 'canceled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(default=timezone.now)
