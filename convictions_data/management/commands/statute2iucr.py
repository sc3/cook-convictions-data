import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Conviction
from convictions_data.statute import (get_iucr, IUCRLookupError,
    ILCSLookupError, StatuteFormatError)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Try converting statute to IUCR"

    def handle(self, *args, **options):
        with transaction.atomic():
            for conviction in Conviction.objects.all():
                changed = False

                if conviction.ammndchargstatute:
                    conviction.final_statute = conviction.ammndchargstatute
                    changed = True
                elif conviction.statute:
                    conviction.final_statute = conviction.statute
                    changed = True

                if conviction.final_statute:
                    try:
                        if conviction.final_statute:
                            offenses = get_iucr(conviction.final_statute)
                            if len(offenses) == 1:
                                conviction.iucr_code = offenses[0].code
                                conviction.iucr_category = offenses[0].offense_category
                                changed = True
                            else:
                                logger.warn("Multiple matching IUCR offenses found for statute '{}'".format(conviction.final_statute))

                    except IUCRLookupError as e:
                        logger.warn(e)
                    except ILCSLookupError as e:
                        logger.warn(e)
                    except AssertionError as e:
                        logger.warn(e)
                    except StatuteFormatError as e:
                        logger.warn(e)

                if changed:
                    conviction.save()
