import json

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

class Command(BaseCommand):
    args = "<model>"
    help = ("Export a JSON file of total convictions and convictions by "
            "major cateogries broken down by age buckets")

    def handle(self, *args, **options):
        convictions_by_age = Conviction.objects.counts_by_age_range()
        self.stdout.write(json.dumps(convictions_by_age))
