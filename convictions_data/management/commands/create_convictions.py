from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Conviction, Disposition

class Command(BaseCommand):
    help = "Create convictions based on disposition records"

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help="Delete previously created models",
        ),
    )

    def handle(self, *args, **options):
        if options['delete']:
            Conviction.objects.all().delete()
            Disposition.objects.in_analysis().update(conviction=None)

        qs = Disposition.objects.in_analysis().filter(chrgclass__regex=r'^[A-Z0-9]{0,1}$')
        
        with transaction.atomic():
            qs.create_convictions() 
