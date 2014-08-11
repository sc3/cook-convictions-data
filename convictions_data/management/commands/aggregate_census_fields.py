from django.core.management.base import BaseCommand

from convictions_data.models import CommunityArea

class Command(BaseCommand):
    help = "Aggregate census fields from tracts to the community area level"

    def handle(self, *args, **options):
        CommunityArea.objects.aggregate_census_fields()
