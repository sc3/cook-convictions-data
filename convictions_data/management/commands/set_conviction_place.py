from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Conviction, Disposition

class Command(BaseCommand):
    help = "Create convictions based on disposition records"

    def handle(self, *args, **options):
        with transaction.atomic():
            for c in Conviction.objects.all():
                # All records in a case should have the same address and therefore
                # the same place.  We can just grab the same one.
                disp = Disposition.objects.filter(case_number=c.case_number)[0]

                if disp.place is not None:
                    c.place = disp.place
                    c.save()
               
