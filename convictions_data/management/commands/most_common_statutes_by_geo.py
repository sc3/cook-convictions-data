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
            default=10,
            dest='count',
            help="Show this many statutes"),
        make_option('--model',
            action='store',
            default='CommunityArea',
            dest='model',
            help="Get most common statutes for this model"),
    )

    def handle(self, *args, **options):
        statute_fieldnames = []
        model_cls = getattr(convictions_data.models, options['model'])
        if options['model'] == 'CommunityArea' :
            model_fieldnames = ['name', 'number']
        else:
            model_fieldnames = ['name',]

        for i in range(1, options['count'] + 1):
            statute_fieldnames.append('_statute_' + str(i))
            statute_fieldnames.append('_chrgdesc_' + str(i))
            statute_fieldnames.append('_count_' + str(i))
            statute_fieldnames.append('_pct_' + str(i))
        fieldnames = model_fieldnames + statute_fieldnames 
        writer = csv.DictWriter(self.stdout,
            fieldnames=fieldnames)

        writer.writeheader()

        qs = model_cls.objects.all()
        if options['model'] == 'CensusPlace':
            # For census places, we only want places in Cook County
            qs = qs.filter(in_cook_county=True).exclude(name="Chicago")
        qs = qs.with_conviction_annotations()

        for ca in qs:
            num_convictions = ca.num_convictions
            row = {fn: getattr(ca, fn) for fn in model_fieldnames}
            top_statutes = ca.most_common_statutes(options['count'])
            for i, statute in enumerate(top_statutes):
                row['_statute_' + str(i+1)] = statute['statute']
                row['_chrgdesc_' + str(i+1)] = statute['chrgdesc']
                row['_count_' + str(i+1)] = statute['count']
                row['_pct_' + str(i+1)] = statute['count'] / num_convictions
            writer.writerow(row)
