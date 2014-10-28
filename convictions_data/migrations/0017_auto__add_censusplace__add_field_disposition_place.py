# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CensusPlace'
        db.create_table('convictions_data_censusplace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('total_population', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('total_population_moe', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('per_capita_income', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('per_capita_income_moe', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('statefp10', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('placefp10', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('placens10', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('geoid10', self.gf('django.db.models.fields.CharField')(max_length=11, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=7, db_index=True)),
            ('namelsad10', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('lsad10', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('classfp10', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('pcicbsa10', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('pcinecta10', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('mtfcc10', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('funcstat10', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('aland10', self.gf('django.db.models.fields.FloatField')()),
            ('awater10', self.gf('django.db.models.fields.FloatField')()),
            ('intptlat10', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('intptlon10', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('boundary', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('convictions_data', ['CensusPlace'])

        # Adding field 'Disposition.place'
        db.add_column('convictions_data_disposition', 'place',
                      self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, to=orm['convictions_data.CensusPlace'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'CensusPlace'
        db.delete_table('convictions_data_censusplace')

        # Deleting field 'Disposition.place'
        db.delete_column('convictions_data_disposition', 'place_id')


    models = {
        'convictions_data.censusplace': {
            'Meta': {'object_name': 'CensusPlace'},
            'aland10': ('django.db.models.fields.FloatField', [], {}),
            'awater10': ('django.db.models.fields.FloatField', [], {}),
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'classfp10': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'funcstat10': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'geoid10': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intptlat10': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'intptlon10': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'lsad10': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'mtfcc10': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7', 'db_index': 'True'}),
            'namelsad10': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pcicbsa10': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'pcinecta10': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'per_capita_income': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'per_capita_income_moe': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'placefp10': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'placens10': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'statefp10': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'total_population': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'total_population_moe': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'convictions_data.censustract': {
            'Meta': {'object_name': 'CensusTract'},
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'to': "orm['convictions_data.CommunityArea']", 'null': 'True'}),
            'community_area_number': ('django.db.models.fields.IntegerField', [], {}),
            'countyfp10': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'geoid10': ('django.db.models.fields.CharField', [], {'max_length': '11', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'per_capita_income': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'per_capita_income_moe': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'statefp10': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'total_population': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'total_population_moe': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'tractce10': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'convictions_data.communityarea': {
            'Meta': {'object_name': 'CommunityArea'},
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'per_capita_income': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'per_capita_income_moe': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_len': ('django.db.models.fields.FloatField', [], {}),
            'total_population': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'total_population_moe': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'convictions_data.conviction': {
            'Meta': {'object_name': 'Conviction'},
            'case_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'chrgdispdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'to': "orm['convictions_data.CommunityArea']", 'null': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80'}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'final_chrgclass': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '1'}),
            'final_chrgdesc': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '50'}),
            'final_chrgtype': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '1'}),
            'final_statute': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iucr_category': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '50'}),
            'iucr_code': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '4'}),
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
            'chrgdispdate': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True'}),
            'chrgtype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'chrgtype2': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'community_area': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'to': "orm['convictions_data.CommunityArea']", 'null': 'True'}),
            'conviction': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'to': "orm['convictions_data.Conviction']", 'null': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80'}),
            'ctlbkngno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fbiidno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fgrprntno': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'final_chrgclass': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '1'}),
            'final_chrgdesc': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '50'}),
            'final_chrgtype': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '1'}),
            'final_statute': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True'}),
            'iucr_category': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '50'}),
            'iucr_code': ('django.db.models.fields.CharField', [], {'default': "''", 'db_index': 'True', 'max_length': '4'}),
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
            'place': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'to': "orm['convictions_data.CensusPlace']", 'null': 'True'}),
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