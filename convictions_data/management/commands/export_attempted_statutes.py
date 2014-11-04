import csv

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = ("Export statutes that indicate an attempted offense")

    def handle(self, *args, **options):
        writer = csv.DictWriter(self.stdout,
            fieldnames=['statute'])

        qs = Disposition.objects.filter(statute__icontains="8-4")
        qs = qs.values('statute').distinct()

        writer.writeheader()

        for disp in qs: 
            writer.writerow(disp)
