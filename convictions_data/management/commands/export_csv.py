import csv

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = ("Export disposition records to CSV removing personal information.")

    def handle(self, *args, **options):
        writer = csv.DictWriter(self.stdout,
            fieldnames=Disposition.objects.EXPORT_FIELDS)

        for disp in Disposition.objects.anonymized_values():
            writer.writerow(disp)
