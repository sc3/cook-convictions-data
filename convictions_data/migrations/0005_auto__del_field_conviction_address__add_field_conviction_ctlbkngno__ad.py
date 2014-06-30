# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Conviction.address'
        db.delete_column('convictions_data_conviction', 'address')

        # Adding field 'Conviction.ctlbkngno'
        db.add_column('convictions_data_conviction', 'ctlbkngno',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'Conviction.fgrprntno'
        db.add_column('convictions_data_conviction', 'fgrprntno',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'Conviction.statepoliceid'
        db.add_column('convictions_data_conviction', 'statepoliceid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'Conviction.fbiidno'
        db.add_column('convictions_data_conviction', 'fbiidno',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'Conviction.st_address'
        db.add_column('convictions_data_conviction', 'st_address',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'Conviction.initial_date'
        db.add_column('convictions_data_conviction', 'initial_date',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'Conviction.sex'
        db.add_column('convictions_data_conviction', 'sex',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)

        # Adding field 'Conviction.statute'
        db.add_column('convictions_data_conviction', 'statute',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Conviction.chrgdesc'
        db.add_column('convictions_data_conviction', 'chrgdesc',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Conviction.chrgtype'
        db.add_column('convictions_data_conviction', 'chrgtype',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1),
                      keep_default=False)

        # Adding field 'Conviction.chrgtype2'
        db.add_column('convictions_data_conviction', 'chrgtype2',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=15),
                      keep_default=False)

        # Adding field 'Conviction.chrgclass'
        db.add_column('convictions_data_conviction', 'chrgclass',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1),
                      keep_default=False)

        # Adding field 'Conviction.chrgdisp'
        db.add_column('convictions_data_conviction', 'chrgdisp',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30),
                      keep_default=False)

        # Adding field 'Conviction.ammndchargstatute'
        db.add_column('convictions_data_conviction', 'ammndchargstatute',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Conviction.ammndchrgdescr'
        db.add_column('convictions_data_conviction', 'ammndchrgdescr',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Conviction.ammndchrgtype'
        db.add_column('convictions_data_conviction', 'ammndchrgtype',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1),
                      keep_default=False)

        # Adding field 'Conviction.ammndchrgclass'
        db.add_column('convictions_data_conviction', 'ammndchrgclass',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1),
                      keep_default=False)

        # Adding field 'Conviction.minsent'
        db.add_column('convictions_data_conviction', 'minsent',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Conviction.maxsent'
        db.add_column('convictions_data_conviction', 'maxsent',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'Conviction.amtoffine'
        db.add_column('convictions_data_conviction', 'amtoffine',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Conviction.address'
        raise RuntimeError("Cannot reverse this migration. 'Conviction.address' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Conviction.address'
        db.add_column('convictions_data_conviction', 'address',
                      self.gf('django.db.models.fields.CharField')(max_length=200),
                      keep_default=False)

        # Deleting field 'Conviction.ctlbkngno'
        db.delete_column('convictions_data_conviction', 'ctlbkngno')

        # Deleting field 'Conviction.fgrprntno'
        db.delete_column('convictions_data_conviction', 'fgrprntno')

        # Deleting field 'Conviction.statepoliceid'
        db.delete_column('convictions_data_conviction', 'statepoliceid')

        # Deleting field 'Conviction.fbiidno'
        db.delete_column('convictions_data_conviction', 'fbiidno')

        # Deleting field 'Conviction.st_address'
        db.delete_column('convictions_data_conviction', 'st_address')

        # Deleting field 'Conviction.initial_date'
        db.delete_column('convictions_data_conviction', 'initial_date')

        # Deleting field 'Conviction.sex'
        db.delete_column('convictions_data_conviction', 'sex')

        # Deleting field 'Conviction.statute'
        db.delete_column('convictions_data_conviction', 'statute')

        # Deleting field 'Conviction.chrgdesc'
        db.delete_column('convictions_data_conviction', 'chrgdesc')

        # Deleting field 'Conviction.chrgtype'
        db.delete_column('convictions_data_conviction', 'chrgtype')

        # Deleting field 'Conviction.chrgtype2'
        db.delete_column('convictions_data_conviction', 'chrgtype2')

        # Deleting field 'Conviction.chrgclass'
        db.delete_column('convictions_data_conviction', 'chrgclass')

        # Deleting field 'Conviction.chrgdisp'
        db.delete_column('convictions_data_conviction', 'chrgdisp')

        # Deleting field 'Conviction.ammndchargstatute'
        db.delete_column('convictions_data_conviction', 'ammndchargstatute')

        # Deleting field 'Conviction.ammndchrgdescr'
        db.delete_column('convictions_data_conviction', 'ammndchrgdescr')

        # Deleting field 'Conviction.ammndchrgtype'
        db.delete_column('convictions_data_conviction', 'ammndchrgtype')

        # Deleting field 'Conviction.ammndchrgclass'
        db.delete_column('convictions_data_conviction', 'ammndchrgclass')

        # Deleting field 'Conviction.minsent'
        db.delete_column('convictions_data_conviction', 'minsent')

        # Deleting field 'Conviction.maxsent'
        db.delete_column('convictions_data_conviction', 'maxsent')

        # Deleting field 'Conviction.amtoffine'
        db.delete_column('convictions_data_conviction', 'amtoffine')


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
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['convictions_data.CommunityArea']", 'null': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80'}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'maxsent': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'minsent': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'raw_conviction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['convictions_data.RawConviction']"}),
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
        'convictions_data.rawconviction': {
            'Meta': {'object_name': 'RawConviction'},
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