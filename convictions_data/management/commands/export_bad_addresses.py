from csv import DictWriter

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = "Export a list of dispositions with ungeocodeable addresses to CSV"

    def handle(self, *args, **options):
        models = Disposition.objects.has_bad_address()

        fields = ['id', 'address', 'city', 'state', 'raw_citystate', 'zipcode']
        writer = DictWriter(self.stdout, fields)
        writer.writeheader()

        for disposition in models:
            writer.writerow({
                'id': disposition.id,
                'address': disposition.address,
                'city': disposition.city,
                'state': disposition.state,
                'zipcode': disposition.zipcode,
                'raw_citystate': disposition.raw_disposition.city_state,
            })
        
