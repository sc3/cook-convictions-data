import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Disposition
from convictions_data.statute import (get_iucr, IUCRLookupError,
    ILCSLookupError, StatuteFormatError)

from pprint import pprint
import json

# can't find a handler?
#logger = logging.getLogger(__name__)


def append_or_create(dict, chrgdesc, category):
    if category:
        try:
            categories = dict[chrgdesc]
            if category not in categories:
                dict[chrgdesc].append(category)
        except KeyError:
            dict[chrgdesc] = [category]
    else:
        # warn if there's no IUCR category for this disposition
        assert False

class Command(BaseCommand):
    help = "Map charge descriptions to iucr categories."

    def handle(self, *args, **options):

        chrgdesc_to_category = {}

        for disposition in Disposition.objects.all():

            chrgdesc = disposition.ammndchrgdescr if \
                    disposition.ammndchrgdescr else disposition.chrgdesc
            category = disposition.iucr_category

            case_number = disposition.case_number
            statute = disposition.final_statute if \
                    disposition.final_statute else disposition.statute
            chrgdisp = disposition.chrgdisp
            chrgdispdate = disposition.chrgdispdate

            try:
                append_or_create(chrgdesc_to_category, chrgdesc, category)
            except AssertionError:
                # print('No IUCR category for disposition: {} {} {} {}'
                #         .format(case_number, statute, chrgdispdate, chrgdisp))
                pass

        print('num total: ', len(chrgdesc_to_category))
        with open('chrgdesc_to_category__all.json', 'w') as f:
            json.dump(chrgdesc_to_category, f)

        chrgdesc_to_category = {x: chrgdesc_to_category[x] for x in chrgdesc_to_category.keys() if len(chrgdesc_to_category[x]) > 1}
        
        with open('chrgdesc_to_category__multiples.json', 'w') as f:
            print('num with multiple: ', len(chrgdesc_to_category))
            json.dump(chrgdesc_to_category, f)




