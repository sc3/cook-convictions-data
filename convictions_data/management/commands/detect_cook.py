from django.core.management.base import BaseCommand

from convictions_data.models import Conviction, Municipality

class Command(BaseCommand):
    help = "Set the county attribute for convictions with home addresses in Cook County"
   
    def handle(self, *args, **options):
        municipality_names = [m['municipality_name'].upper() for
                              m in
                              Municipality.objects.all().values('municipality_name')
                              if m['municipality_name']]
        cook_convictions = Conviction.objects.filter(city__in=municipality_names)
        cook_convictions.update(county="Cook")
