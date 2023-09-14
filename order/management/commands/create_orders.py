import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from order.models import Order, OrderStatus


class Command(BaseCommand):
    help = "Generate sample orders"

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='?', type=int, default=1000)

    def handle(self, *args, **options):
        Order.objects.all().delete()
        for i in range(options['count']):
            order = Order()
            order.save()
            for j in range(random.randint(-5, 5)):
                if j < 0:
                    break
                status = random.choice(OrderStatus.Status.choices)[0]
                created = timezone.now() - timezone.timedelta(days=random.randint(0, 1000))
                order_status = OrderStatus(order=order, status=status, created=created)
                order_status.save()
