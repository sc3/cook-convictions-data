# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Conviction'
        db.create_table('convictions_data_conviction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case_number', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('ctlbkngno', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fgrprntno', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('statepoliceid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fbiidno', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True)),
            ('st_address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=80, default='')),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
            ('chrgdispdate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('final_statute', self.gf('django.db.models.fields.CharField')(max_length=50, default='', db_index=True)),
            ('iucr_code', self.gf('django.db.models.fields.CharField')(max_length=4, default='', db_index=True)),
            ('iucr_category', self.gf('django.db.models.fields.CharField')(max_length=50, default='', db_index=True)),
            ('community_area', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['convictions_data.CommunityArea'])),
        ))
        db.send_create_signal('convictions_data', ['Conviction'])

        # Adding field 'Disposition.conviction'
        db.add_column('convictions_data_disposition', 'conviction',
                      self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['convictions_data.Conviction']),
                      keep_default=False)

        # Adding index on 'Disposition', fields ['iucr_category']
        db.create_index('convictions_data_disposition', ['iucr_category'])

        # Adding index on 'Disposition', fields ['initial_date']
        db.create_index('convictions_data_disposition', ['initial_date'])

        # Adding index on 'Disposition', fields ['chrgdispdate']
        db.create_index('convictions_data_disposition', ['chrgdispdate'])

        # Adding index on 'Disposition', fields ['iucr_code']
        db.create_index('convictions_data_disposition', ['iucr_code'])

        # Adding index on 'Disposition', fields ['final_statute']
        db.create_index('convictions_data_disposition', ['final_statute'])

        # Adding index on 'Disposition', fields ['case_number']
        db.create_index('convictions_data_disposition', ['case_number'])


    def backwards(self, orm):
        # Removing index on 'Disposition', fields ['case_number']
        db.delete_index('convictions_data_disposition', ['case_number'])

        # Removing index on 'Disposition', fields ['final_statute']
        db.delete_index('convictions_data_disposition', ['final_statute'])

        # Removing index on 'Disposition', fields ['iucr_code']
        db.delete_index('convictions_data_disposition', ['iucr_code'])

        # Removing index on 'Disposition', fields ['chrgdispdate']
        db.delete_index('convictions_data_disposition', ['chrgdispdate'])

        # Removing index on 'Disposition', fields ['initial_date']
        db.delete_index('convictions_data_disposition', ['initial_date'])

        # Removing index on 'Disposition', fields ['iucr_category']
        db.delete_index('convictions_data_disposition', ['iucr_category'])

        # Deleting model 'Conviction'
        db.delete_table('convictions_data_conviction')

        # Deleting field 'Disposition.conviction'
        db.delete_column('convictions_data_disposition', 'conviction_id')


    models = {
        'convictions_data.communityarea': {
            'Meta': {'object_name': 'CommunityArea'},
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_len': ('django.db.models.fields.FloatField', [], {})
        },
        'convictions_data.conviction': {
            'Meta': {'object_name': 'Conviction'},
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'chrgdispdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['convictions_data.CommunityArea']"}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '80', 'default': "''"}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'final_statute': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''", 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iucr_category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''", 'db_index': 'True'}),
            'iucr_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'default': "''", 'db_index': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'st_address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'statepoliceid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'convictions_data.disposition': {
            'Meta': {'object_name': 'Disposition'},
            'ammndchargstatute': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ammndchrgclass': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ammndchrgdescr': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ammndchrgtype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'amtoffine': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'arrest_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'chrgclass': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'chrgdesc': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'chrgdisp': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'chrgdispdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_index': 'True'}),
            'chrgtype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'chrgtype2': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['convictions_data.CommunityArea']"}),
            'conviction': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['convictions_data.Conviction']"}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '80', 'default': "''"}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'final_statute': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''", 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_index': 'True'}),
            'iucr_category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''", 'db_index': 'True'}),
            'iucr_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'default': "''", 'db_index': 'True'}),
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