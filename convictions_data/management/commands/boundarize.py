from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = "Detect community area of geocoded disposition"

    def handle(self, *args, **options):
        # Only detect boundaries for dispositions that don't have a community
        # area set.
        models = Disposition.objects.geocoded().filter(community_area=None)
        i = 1
        for disposition in models:
            msg = "Detecting boundaries of disposition {}/{} ... ".format(i,
                models.count())
            self.stdout.write(msg, ending='')                

            if disposition.boundarize():
                self.stdout.write("Done") 
            else:
                self.stdout.write("Failed")

            i += 1
