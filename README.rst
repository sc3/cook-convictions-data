=====================
cook-convictions-data
=====================

A simple Django project for loading, cleaning and querying Cook County Illinois convictions data.

This is the preprocessing backend that drives the presentation of https://github.com/sc3/cook-convictions/

Quickstart
==========

Installation
------------

::

    git clone https://github.com/sc3/cook-convictions-data.git
    mkvirtualenv convictions
    cd django-convictions
    pip install -r requirements.txt
    cp convictions/setttings/dev.example.py convictions/settings/dev.py
    # Edit convictions/settings/dev.py to fill in the needed variables
    spatialite convictions.sqlite3 "SELECT InitSpatialMetaData();"
    ./manage.py syncdb
    ./manage.py migrate

Load spatial data
-----------------

First, download and unpack the Shapefile version of the Cook County Municipalities data from https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Municipality/ta8t-zebk

Then run::

    ./manage.py load_spatial_data Municipality data/Municipality/Municipality.shp

Download and unpack the Shapefile version of the Census Tract data.

Then run::

    ./manage.py load_spatial_data CensusTract data/CensusTracts2010/CensusTractsTIGER2010.shp

Load raw dispositions data
-------------------------

::

    ./manage.py load_dispositions_csv data/Criminal_Convictions_ALLCOOK_05-09.csv


Populate clean disposition records
----------------------------------

::

    ./manage.py create_dispositions

Geocode disposition records
---------------------------

::

    ./manage.py geocode_dispositions

Load census data
----------------

::

    ./manage.py load_aff_data data/ACS_10_5YR_B01003_with_ann-totpop.csv total_population GEO.id2 HD01_VD01 HD02_VD01 

    ./manage.py load_aff_data data/ACS_10_5YR_B19301_with_ann-per_capita_income.csv per_capita_income GEO.id2 HD01_VD01 HD02_VD01


Extract Chicago's border from a shapefile
-----------------------------------------

::

    ./manage.py chicago_geojson_from_shp data/tl_2010_17_place10/tl_2010_17_place10.shp > chicago.json 


Other datasets
==============

* `Boundaries - Community Areas (current) <https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6>`_ 
* `Cook County Municipalities <https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Municipality/ta8t-zebk>`_
* `2010 Illinois Census Place TIGER Shapefile <http://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_17_place10.zip>`_
* `Boundaries - Census Tracts - 2010 <https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Census-Tracts-2010/5jrd-6zik>`_
