import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

class Command(BaseCommand):
    help = ("Export CSV table showing most common conviction statutes")
    option_list = BaseCommand.option_list + (
        make_option('--count',
            action='store',
            type='int',
            default=10,
            dest='count',
            help="Show this many statutes"),
    )

    def handle(self, *args, **options):
        fieldnames = ['statute', 'chrgdesc', 'count']
        writer = csv.DictWriter(self.stdout,
            fieldnames=fieldnames)

        writer.writeheader()

        for row in Conviction.objects.all().most_common_statutes(options['count']):
            writer.writerow(row)
