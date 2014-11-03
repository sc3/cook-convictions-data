import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import CommunityArea 

class Command(BaseCommand):
    help = ("Export CSV table showing most common conviction statute by geography")
    option_list = BaseCommand.option_list + (
        make_option('--count',
            action='store',
            type='int',
            default=10,
            dest='count',
            help="Show this many statutes"),
    )

    def handle(self, *args, **options):
        statute_fieldnames = ['statute_' + str(i) 
            for i in range(1, options['count'] + 1)]
        fieldnames = ['community_area', 'number'] + statute_fieldnames 
        writer = csv.DictWriter(self.stdout,
            fieldnames=fieldnames)

        writer.writeheader()

        for ca in CommunityArea.objects.all():
            row = {
                'community_area': ca.name,
                'number': ca.number,
            }
            top_statutes = ca.most_common_statutes(options['count'])
            for i, statute in enumerate(top_statutes):
                row['statute_' + str(i+1)] = statute['chrgdesc']
            writer.writerow(row)
