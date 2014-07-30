from django.core.management.base import BaseCommand

from convictions_data.models import Disposition, Municipality

class Command(BaseCommand):
    help = "Set the county attribute for dispositions with home addresses in Cook County"
   
    def handle(self, *args, **options):
        municipality_names = [m['municipality_name'].upper() for
                              m in
                              Municipality.objects.all().values('municipality_name')
                              if m['municipality_name']]
        cook_dispositions = Disposition.objects.filter(city__in=municipality_names)
        cook_dispositions.update(county="Cook")
