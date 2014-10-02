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

Download and unpack the Shapefile version of the Illinois Census Places data.

Then run::

    ./manage.py load_spatial_data CensusPlace data/tl_2010_17_place10/tl_2010_17_place10.shp

Load raw dispositions data
--------------------------

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

    ./manage.py load_aff_data CensusTract total_population GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B01003_with_ann__totpop__tracts.csv

    ./manage.py load_aff_data CensusTract per_capita_income GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B19301_with_ann__per_capita_income__tracts.csv

    ./manage.py load_aff_data CensusPlace total_population GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B01003_with_ann__totpop__places.csv

    ./manage.py load_aff_data CensusPlace per_capita_income GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B19301_with_ann__per_capita_income__places.csv

Export Community Area and Census Place GeoJSON
----------------------------------------------

::

    ./manage.py export_model_geojson CommunityArea > community_areas.json

    ./manage.py export_model_geojson CensusPlace > suburbs.json


Extract Chicago's border from a shapefile
-----------------------------------------

::

    ./manage.py chicago_geojson_from_shp data/tl_2010_17_place10/tl_2010_17_place10.shp > chicago.json 

Export convictions by age bucket
--------------------------------

::

   ./manage.py export_age_json > convictions_by_age.json


Manual Processes
================

Creating a list of suburban places
----------------------------------

It's hard to define Chicago Suburbs.  I made the decision to define these as Census Places in the counties that are part of Chicago's Metropolitan Statistical Area:

* Cook
* DeKalb
* DuPage
* Grundy
* Kane
* Kendall
* McHenry
* Will
* Lake

I created a list of these census places by bringing the TIGER shapefile for Illinois counties into QGIS.  I paired this down to the counties above.  Then, I used the "Join Attributes by Location" vector data management tool to create a shapefile of only census places within these counties.  Finally, I extracted the attributes from the shapefile as a CSV like this:

::

     ogr2ogr -f CSV tl_2010_17_place10_chicago_msa.csv tl_2010_17_place10_chicago_msa/tl_2010_17_place10_chicago_msa.shp

Loading conviction places from dispositions
-------------------------------------------

Because we added places mid-process, I didn't want to re-create Conviction records.  I wrote a one-off management command to copy the places from the dispositions::

    ./manage.py set_conviction_place


Other datasets
==============

* `Boundaries - Community Areas (current) <https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6>`_ 
* `Cook County Municipalities <https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Municipality/ta8t-zebk>`_
* `Boundaries - Census Tracts - 2010 <https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Census-Tracts-2010/5jrd-6zik>`_
* `2010 Illinois Census Place TIGER Shapefile <http://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_17_place10.zip>`_
* 2010 ACS 5-year Estimates "TOTAL POPULATION" (B01003) for Cook County Census Tracts
* 2010 ACS 5-year Estimates "TOTAL POPULATION" (B01003) for Illinois Census Places 
* 2010 ACS 5-year Estimates "PER CAPITA INCOME IN THE PAST 12 MONTHS (IN 2010 INFLATION-ADJUSTED DOLLARS)" (B19301) for Cook County Census Tracts
* `2010 ACS 5-year Estimates "PER CAPITA INCOME IN THE PAST 12 MONTHS (IN 2010 INFLATION-ADJUSTED DOLLARS)" (B19301) for Illinois Census Places <http://factfinder2.census.gov/faces/tableservices/jsf/pages/productview.xhtml?pid=ACS_10_5YR_B19301&prodType=table>`_
