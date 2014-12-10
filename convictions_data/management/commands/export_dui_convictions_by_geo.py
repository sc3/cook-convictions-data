import csv
from optparse import make_option

from django.core.management.base import BaseCommand

import convictions_data.models

class Command(BaseCommand):
    help = ("Export CSV table showing most common conviction statute by geography")
    option_list = BaseCommand.option_list + (
        make_option('--count',
            action='store',
            type='int',
            default=20,
            dest='count',
            help="Show this many statutes"),
        make_option('--model',
            action='store',
            default='CommunityArea',
            dest='model',
            help="Get most common statutes for this model"),
    )

    def handle(self, *args, **options):
        model_cls = getattr(convictions_data.models, options['model'])
        qs = model_cls.objects.all().with_dui_annotations().order_by('-num_dui')
       
        fieldnames = ['name', 'count', 'pct'] 
        writer = csv.DictWriter(self.stdout,
            fieldnames=fieldnames)

        writer.writeheader()

        for geo in qs[:options['count']]:
            row = {
                'name': geo.name,
                'count': geo.num_dui,
                'pct': geo.pct_dui,
            }
            writer.writerow(row)
