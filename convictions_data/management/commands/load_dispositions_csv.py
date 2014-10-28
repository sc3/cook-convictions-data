import csv
import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import RawDisposition

class Command(BaseCommand):
    args = "<csv_filename>"
    help = "Load raw dispositions CSV into database models"

    # Number of records to insert at once as it fails if we try to insert
    # all the records at once
    BATCH_SIZE = 5000

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help="Delete previously loaded models",
        ),
        make_option('--batch-size',
            action='store',
            type='int',
            default=BATCH_SIZE,
            dest='batch_size',
            help="Process in batches of this number of records"),
    )

    def handle(self, *args, **options):
        csv_filename = args[0]

        if options['delete']:
            RawDisposition.objects.all().delete()

        with open(csv_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            models = []
            for row in reader:
                model_kwargs = {k.lower():v for k, v in row.items()}
                models.append(RawDisposition(**model_kwargs))

        for i in range(0, len(models), options['batch_size']):
            RawDisposition.objects.bulk_create(models[i:i+options['batch_size']])

        self.fix_shifted()

    def fix_shifted(self):
        """Fix columns that were shifted due to bad escaping in the CSV"""
        # HACK: This is overly verbose and could be generalized.  For now,
        # just do this explicitly, but if we run into more examples that need
        # this, we should make a more general solution for shifting columns

        # TODO: Move this into a separate management command
        bad_chrgdesc = "RIFLE <16''/SHOTGUN <18\",F\""
        disps = RawDisposition.objects.filter(chrgdesc=bad_chrgdesc)
        for disp in disps:
            disp.amtoffine = disp.maxsent
            disp.maxsent = disp.minsent
            disp.ammndchrgclass = disp.ammndchrgtype
            disp.ammndchrgtype = disp.ammndchrgdescr
            disp.ammndchrgdescr = disp.ammndchargstatute
            disp.ammndchargstatute = disp.chrgdispdate
            disp.chrgdispdate = disp.chrgdisp
            disp.chrgdisp = disp.chrgclass
            disp.chrgclass = disp.chrgtype2
            disp.chrgtype2 = disp.chrgtype
            disp.chrgtype = "F"
            disp.chrgdesc = "RIFLE <16''/SHOTGUN <18\""
            logging.info("Fixing shifted cells due to chrgdesc in RawDisposition "
                "with pk {}".format(disp.pk))
            disp.save()

        disps = RawDisposition.objects.filter(ammndchrgdescr=bad_chrgdesc)
        for disp in disps:
            disp.amtoffine = disp.maxsent
            disp.maxsent = disp.minsent
            disp.ammndchrgclass = disp.ammndchrgtype
            disp.ammndchrgtype = "F"
            disp.ammndchrgdescr = "RIFLE <16''/SHOTGUN <18\""
            logging.info("Fixing shifted cells due to ammndchrgdescr in RawDisposition "
                "with pk {}".format(disp.pk))
            disp.save()

        bad_address = "10716 S AVENUE M\",CHICAGO     IL\""
        disps = RawDisposition.objects.filter(st_address=bad_address)
        for disp in disps:
            disp.amtoffine = disp.maxsent
            disp.maxsent = disp.minsent
            disp.ammndchrgclass = disp.ammndchrgtype
            disp.ammndchrgtype = disp.ammndchrgdescr
            disp.ammndchrgdescr = disp.ammndchargstatute
            disp.ammndchargstatute = disp.chrgdispdate
            disp.chrgdispdate = disp.chrgdisp
            disp.chrgdisp = disp.chrgclass
            disp.chrgclass = disp.chrgtype2
            disp.chrgtype2 = disp.chrgtype
            disp.chrgtype = disp.chrgdesc
            disp.chrgdesc = disp.statute
            disp.statute = disp.sex
            disp.sex = disp.initial_date
            disp.initial_date = disp.arrest_date
            disp.arrest_date = disp.dob
            disp.dob = disp.fbiidno
            disp.fbiidno = disp.statepoliceid
            disp.statepoliceid = disp.fgrprntno
            disp.fgrprntno = disp.ctlbkngno
            disp.ctlbkngno = disp.zipcode
            disp.zipcode = disp.city_state
            disp.city_state = "CHICAGO, IL"
            disp.st_address = "10716 S AVENUE M"
            logging.info("Fixing shifted cells due to st_address in RawDisposition "
                "with pk {}".format(disp.pk))
            disp.save()
