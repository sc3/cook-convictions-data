from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

class Command(BaseCommand):
    help = "Reload conviction records from raw records"

    def handle(self, *args, **options):
        models = Conviction.objects.all()
        models.load_from_raw(save=True)
