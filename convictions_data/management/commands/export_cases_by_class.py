import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = ("Export CSV of cases by charge class and year")

    option_list = BaseCommand.option_list + (
        make_option('--filter',
            action='store',
            default='felonies',
            dest='filter',
            help="Queryset filter to use"),
    )

    def _felony_label(self, chrgclass):
        if chrgclass == 'M':
            return "Murder"
        else:
            return "Class {} Felony".format(chrgclass)

    def handle(self, *args, **options):
        filter_method_name = options['filter']
        classes = ['4', '3', '2', '1', 'X', 'M']
        labels = [self._felony_label(cc) for cc in classes]
        writer = csv.writer(self.stdout)
        writer.writerow(['Year'] + labels)
        for yr in range(2005, 2010):
            cols = [yr]
            for chrgclass in classes:
                qs = Disposition.objects.all().initial_date_in_year(yr)
                filter_method = getattr(qs, filter_method_name)
                qs = filter_method()
                cnt = qs.filter(final_chrgclass=chrgclass).num_cases()
               
                cols.append(cnt)

            writer.writerow(cols)
