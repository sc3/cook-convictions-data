from csv import DictWriter

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

class Command(BaseCommand):
    help = "Export a list of convictions with ungeocodeable addresses to CSV"

    def handle(self, *args, **options):
        models = Conviction.objects.has_bad_address()

        fields = ['id', 'address', 'city', 'state', 'raw_citystate', 'zipcode']
        writer = DictWriter(self.stdout, fields)
        writer.writeheader()

        for conviction in models:
            writer.writerow({
                'id': conviction.id,
                'address': conviction.address,
                'city': conviction.city,
                'state': conviction.state,
                'zipcode': conviction.zipcode,
                'raw_citystate': conviction.raw_conviction.city_state,
            })
        
