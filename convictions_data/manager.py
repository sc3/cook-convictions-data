from django.contrib.gis.db import models as geo_models
from django.db import models

from convictions_data.query import (CensusPlaceQueryset, ConvictionGeoQuerySet,
    DispositionQuerySet)

class DispositionManager(models.Manager):
    """Custom manager that uses DispositionQuerySet"""

    def get_query_set(self):
        return DispositionQuerySet(self.model, using=self._db)

    def geocode(self):
        return self.get_query_set().geocode()

    def ungeocoded(self):
        return self.get_query_set().ungeocoded()

    def geocoded(self):
        return self.get_query_set().geocoded()

    def load_from_raw(self, save=False):
        return self.get_query_set().load_from_raw(save)

    def load_field_from_raw(self, field_name, save=False):
        return self.get_query_set().load_field_from_raw(field_name, save)

    def has_bad_address(self):
        return self.get_query_set().has_bad_address()

    def has_geocodable_address(self):
        return self.get_query_set().has_geocodable_address()

    def in_analysis(self):
        return self.get_query_set().in_analysis()


class ConvictionGeoManager(geo_models.GeoManager):
    def get_queryset(self):
        return ConvictionGeoQuerySet(self.model, using=self._db)

    def geojson(self, simplify=0.0):
        return self.get_queryset().geojson(simplify=simplify)

    def convictions_per_capita(self):
        return self.get_queryset().convictions_per_capita()


class CommunityAreaManager(ConvictionGeoManager):
    def aggregate_census_fields(self):
        for ca in self.get_query_set():
            ca.aggregate_census_fields()
            ca.save()


class CensusTractManager(geo_models.GeoManager):
    def set_community_area_relations(self):
        for tract in self.get_query_set().all():
            ca = self.model.get_community_area_model().objects.get(number=tract.community_area_number)
            tract.community_area = ca
            tract.save()


class CensusPlaceManager(ConvictionGeoManager):
    def get_queryset(self):
        return CensusPlaceQueryset(self.model, using=self._db)

    def chicago_suburbs(self):
        return self.get_queryset().chicago_suburbs()
