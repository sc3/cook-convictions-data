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

                try:
                    if conviction.statute:
                        offenses = get_iucr(conviction.statute)
                        if len(offenses) == 1:
                            conviction.iucr_code = offenses[0].code
                            conviction.iucr_category = offenses[0].offense_category
                            changed = True
                        else:
                            logger.warn("Multiple matching IUCR offenses found for statute '{}'".format(conviction.statute))

                    if conviction.ammndchargstatute:
                        offenses = get_iucr(conviction.ammndchargstatute)

                        if len(offenses) == 1:
                            conviction.ammnd_iucr_code = offenses[0].code
                            conviction.ammnd_iucr_category = offenses[0].offense_category
                            changed = True
                        else:
                            logger.warn("Multiple matching IUCR offenses found for ammended statute '{}'".format(conviction.ammndchargstatute))

                    if changed:
                        conviction.save()

                except IUCRLookupError as e:
                    logger.warn(e)
                except ILCSLookupError as e:
                    logger.warn(e)
                except AssertionError as e:
                    logger.warn(e)
                except StatuteFormatError as e:
                    logger.warn(e)
