# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RawConviction'
        db.create_table('convictions_data_rawconviction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sequence_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('st_address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city_state', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ctlbkngno', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fgrprntno', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('statepoliceid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fbiidno', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('dob', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('arrest_date', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('initial_date', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('statute', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('chrgdesc', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('chrgtype', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('chrgtype2', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('chrgclass', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('chrgdisp', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('chrgdispdate', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ammndchargstatute', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ammndchrgdescr', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ammndchrgtype', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ammndchrgclass', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('minsent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('maxsent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('amtoffine', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('convictions_data', ['RawConviction'])

        # Adding model 'Conviction'
        db.create_table('convictions_data_conviction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_conviction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['convictions_data.RawConviction'])),
            ('case_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sequence_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True)),
            ('arrest_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('chrgdispdate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('lon', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal('convictions_data', ['Conviction'])

        # Adding model 'Municipality'
        db.create_table('convictions_data_municipality', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agency_id', self.gf('django.db.models.fields.IntegerField')()),
            ('agency_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('municipality_name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('st_area', self.gf('django.db.models.fields.FloatField')()),
            ('sde_length', self.gf('django.db.models.fields.FloatField')()),
            ('shape_area', self.gf('django.db.models.fields.FloatField')()),
            ('shape_length', self.gf('django.db.models.fields.FloatField')()),
            ('boundary', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('convictions_data', ['Municipality'])


    def backwards(self, orm):
        # Deleting model 'RawConviction'
        db.delete_table('convictions_data_rawconviction')

        # Deleting model 'Conviction'
        db.delete_table('convictions_data_conviction')

        # Deleting model 'Municipality'
        db.delete_table('convictions_data_municipality')


    models = {
        'convictions_data.conviction': {
            'Meta': {'object_name': 'Conviction'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'arrest_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'chrgdispdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'raw_conviction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['convictions_data.RawConviction']"}),
            'sequence_number': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
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