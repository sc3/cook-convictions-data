import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Disposition
from convictions_data.statute import (get_iucr, IUCRLookupError,
    ILCSLookupError, StatuteFormatError)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Try converting statute to IUCR"

    def handle(self, *args, **options):
        with transaction.atomic():
            for disposition in Disposition.objects.all():
                changed = False

                if disposition.ammndchargstatute:
                    disposition.final_statute = disposition.ammndchargstatute
                    changed = True
                elif disposition.statute:
                    disposition.final_statute = disposition.statute
                    changed = True

                if disposition.final_statute:
                    try:
                        if disposition.final_statute:
                            offenses = get_iucr(disposition.final_statute)
                            if len(offenses) == 1:
                                disposition.iucr_code = offenses[0].code
                                disposition.iucr_category = offenses[0].offense_category
                                changed = True
                            else:
                                logger.warn("Multiple matching IUCR offenses found for statute '{}'".format(disposition.final_statute))

                    except IUCRLookupError as e:
                        logger.warn(e)
                    except ILCSLookupError as e:
                        logger.warn(e)
                    except AssertionError as e:
                        logger.warn(e)
                    except StatuteFormatError as e:
                        logger.warn(e)

                if changed:
                    disposition.save()
