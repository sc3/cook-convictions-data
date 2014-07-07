from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

class Command(BaseCommand):
    help = "Detect community area of geocoded conviction"

    def handle(self, *args, **options):
        # Only detect boundaries for convictions that don't have a community
        # area set.
        models = Conviction.objects.geocoded().filter(community_area=None)
        i = 1
        for conviction in models:
            msg = "Detecting boundaries of conviction {}/{} ... ".format(i,
                models.count())
            self.stdout.write(msg, ending='')                

            if conviction.boundarize():
                self.stdout.write("Done") 
            else:
                self.stdout.write("Failed")

            i += 1
