import csv
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = ("Export disposition records to CSV removing personal information.")
    option_list = BaseCommand.option_list + (
        make_option('--year',
            action='store',
            type='int',
            default=None,
            dest='year',
            help="Only export records for this year"),
    )

    def handle(self, *args, **options):
        writer = csv.DictWriter(self.stdout,
            fieldnames=Disposition.objects.EXPORT_FIELDS)

        qs = Disposition.objects.all()
        if options['year']:
            assert options['year'] >= 2005 and options['year'] <= 2009
            filter_kwargs = self._get_year_filter_kwargs(options['year'])
            qs = qs.filter(**filter_kwargs).order_by('case_number')

        writer.writeheader()

        for disp in qs.anonymized_values(): 
            writer.writerow(disp)

    def _get_year_filter_kwargs(self, year):
        filter_kwargs = {}
        if year != 2005:
            # Include records with initial dates before our window with 2005
            # That means, don't set a lower bound if the year is 2005
            filter_kwargs['initial_date__gte'] = datetime.date(year, 1, 1)

        filter_kwargs['initial_date__lt'] = datetime.date(year + 1, 1, 1)

        return filter_kwargs
