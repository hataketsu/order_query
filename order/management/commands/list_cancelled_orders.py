from django.core.management.base import BaseCommand

from order.models import Order


class Command(BaseCommand):
    help = "Query orders"

    def handle(self, *args, **options):
        canceled_query = Order.objects.canceled()
        print("Canceled orders query:", canceled_query.query)
        print("Canceled orders count:", canceled_query.count())

        pending_query = Order.objects.pending()
        print("Pending orders query:", pending_query.query)
        print("Pending orders count:", pending_query.count())

        complete_query = Order.objects.complete()
        print("Complete orders query:", complete_query.query)
        print("Complete orders count:", complete_query.count())

        print("All queried orders count:", canceled_query.count() + pending_query.count() + complete_query.count())
        print("Total orders count:", Order.objects.count())
