import csv
from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition

class Command(BaseCommand):
    help = ("Export CSV table of how class changed")

    option_list = BaseCommand.option_list + (
        make_option('--pct',
            action='store_true',
            dest='percentage',
            help="Queryset filter to use"),
    )

    def _chrgclass_label(self, chrgclass):
        if chrgclass == 'M':
            return "Murder"
        elif chrgclass in ['4', '3', '2', '1', 'X']:
            return "Class {} Felony".format(chrgclass)
        else:
            return "Class {} Misdemeanor".format(chrgclass)

    def handle(self, *args, **options):
        felony_classes =  ['4', '3', '2', '1', 'X', 'M']
        misdemeanor_classes = ['C', 'B', 'A']
        classes = misdemeanor_classes + felony_classes
        labels = [self._chrgclass_label(cc) for cc in classes]
        writer = csv.writer(self.stdout)
        writer.writerow([''] + labels)
        qs = Disposition.objects.all().filter(initial_date__gte=datetime(2005, 1, 1))
        for class_from in classes:
            cols = [self._chrgclass_label(class_from)]
            total_from = qs.filter(chrgclass=class_from).num_cases()
            for class_to in classes:
                cnt = qs.filter(chrgclass=class_from, final_chrgclass=class_to).num_cases()
                if options['percentage']:
                    val = cnt / total_from
                else:
                    val = cnt

                cols.append(val)

            writer.writerow(cols)
