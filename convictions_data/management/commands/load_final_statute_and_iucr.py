import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Disposition
from convictions_data.statute import (get_iucr, IUCRLookupError,
    ILCSLookupError, StatuteFormatError)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ("Load the final statute, nicely formatted statute and IUCR code "
            "from the statute or ammended statute fields")

    def handle(self, *args, **options):
        with transaction.atomic():
            for disposition in Disposition.objects.all():
                if disposition.ammndchargstatute:
                    disposition.load_final_statute_and_iucr(disposition.ammndchargstatute)
                    disposition.save()
                elif disposition.statute:
                    disposition.load_final_statute_and_iucr(disposition.statute)
                    disposition.save()
