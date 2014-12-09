import csv

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

class Command(BaseCommand):
    args = "<qs_filter>"
    help = ("Export a table of counts of drug convictions grouped by "
            "class or drug type")

    def handle(self, *args, **options):
        qs_filter = args[0]
        filter_method = getattr(Conviction.objects, qs_filter)
        data = filter_method()
        fieldnames = data[0].keys()
        writer = csv.DictWriter(self.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
