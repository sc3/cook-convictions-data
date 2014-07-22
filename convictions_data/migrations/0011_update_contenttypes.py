# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        if not db.dry_run:
            orm['contenttypes.ContentType'].objects.filter(
                app_label='convictions_data',
                model='rawconviction').update(name='rawdisposition', model='rawdisposition')

        if not db.dry_run:
            orm['contenttypes.ContentType'].objects.filter(
                app_label='convictions_data',
                model='conviction').update(name='disposition', model='disposition')

    def backwards(self, orm):
        if not db.dry_run:
            orm['contenttypes.ContentType'].objects.filter(
                app_label='convictions_data',
                model='rawdisposition').update(name='rawconviction', model='rawconviction')

        if not db.dry_run:
            orm['contenttypes.ContentType'].objects.filter(
                app_label='convictions_data',
                model='disposition').update(name='conviction', model='conviction')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ContentType', 'db_table': "'django_content_type'", 'unique_together': "(('app_label', 'model'),)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'convictions_data.communityarea': {
            'Meta': {'object_name': 'CommunityArea'},
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_len': ('django.db.models.fields.FloatField', [], {})
        },
        'convictions_data.disposition': {
            'Meta': {'object_name': 'Disposition'},
            'ammndchargstatute': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ammndchrgclass': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ammndchrgdescr': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ammndchrgtype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'amtoffine': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'arrest_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgclass': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'chrgdesc': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'chrgdisp': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'chrgdispdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'chrgtype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'chrgtype2': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['convictions_data.CommunityArea']"}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '80', 'default': "''"}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'final_statute': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'iucr_category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''"}),
            'iucr_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'default': "''"}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'maxsent_days': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'maxsent_death': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maxsent_life': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maxsent_months': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'maxsent_years': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'minsent_days': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'minsent_death': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minsent_life': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minsent_months': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'minsent_years': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'raw_disposition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['convictions_data.RawDisposition']"}),
            'sequence_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'st_address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'statepoliceid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'statute': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'convictions_data.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'agency_id': ('django.db.models.fields.IntegerField', [], {}),
            'agency_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality_name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'sde_length': ('django.db.models.fields.FloatField', [], {}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_length': ('django.db.models.fields.FloatField', [], {}),
            'st_area': ('django.db.models.fields.FloatField', [], {})
        },
        'convictions_data.rawdisposition': {
            'Meta': {'object_name': 'RawDisposition'},
            'ammndchargstatute': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ammndchrgclass': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ammndchrgdescr': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ammndchrgtype': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'amtoffine': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'arrest_date': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgclass': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgdesc': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgdisp': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgdispdate': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgtype': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgtype2': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'city_state': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'maxsent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'minsent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sequence_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'st_address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'statepoliceid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'statute': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['convictions_data']
    symmetrical = True
