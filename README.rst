=====================
cook-convictions-data
=====================

A simple Django project for loading, cleaning and querying Cook County Illinois convictions data.

This is the preprocessing backend that drives the presentation of https://github.com/sc3/cook-convictions/

Quickstart
==========

Installation
------------

Create spatial database
~~~~~~~~~~~~~~~~~~~~~~~

PostGIS

::

    $ createdb convictions
    $ psql convictions
    > CREATE EXTENSION postgis;
    > CREATE EXTENSION postgis_topology;

Spatialite

::

    spatialite convictions.sqlite3 "SELECT InitSpatialMetaData();"

::

    git clone https://github.com/sc3/cook-convictions-data.git
    mkvirtualenv convictions
    cd django-convictions
    pip install -r requirements.txt
    cp convictions/setttings/dev.example.py convictions/settings/dev.py
    # Edit convictions/settings/dev.py to fill in the needed variables
    ./manage.py syncdb
    ./manage.py migrate

We use `DataMade's <http://datamade.us/>`_ `usaddress <https://github.com/datamade/usaddress>`_ package to parse addresses when anonymizing them to the block level.  However, the stable version of the package doesn't support Python 3. In a pinch, we use a fork that I made that adds rough Python 3 support.  We install this fork as editable, so we need to do the training.

::

    workon convictions
    cd /path/to/virtualenv/src/usaddress
    python training/training.py


Load spatial data
-----------------

Download and unpack the Shapefile version of Chicago Community Areas.

Then run::

     ./manage.py load_spatial_data CommunityArea data/Comm_20Areas/CommAreas.shp

Download and unpack the Shapefile version of the Cook County Municipalities data from https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Municipality/ta8t-zebk

Then run::

    ./manage.py load_spatial_data Municipality data/Municipality/Municipality.shp

Download and unpack the Shapefile version of the Census Tract data.

Then run::

    ./manage.py load_spatial_data CensusTract data/CensusTracts2010/CensusTractsTIGER2010.shp

Download and unpack the Shapefile version of the Illinois Census Places data.

Then run::

    ./manage.py load_spatial_data CensusPlace data/tl_2010_17_place10/tl_2010_17_place10.shp

Download and unpack the Shapefile version of the Illinois County data.

Then run::

    ./manage.py load_spatial_data County data/tl_2010_17_county10/tl_2010_17_county10.shp

For generating the Chicago and Cook County border GeoJSON file, we use the cartographic versions of the county and place shapefiles because they remove offshore areas.  You'll want to download and unpack those too.

Load census data
----------------

::

    ./manage.py load_aff_data CensusTract total_population GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B01003_with_ann__totpop__tracts.csv

    ./manage.py load_aff_data CensusTract per_capita_income GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B19301_with_ann__per_capita_income__tracts.csv

    ./manage.py load_aff_data CensusPlace total_population GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B01003_with_ann__totpop__places.csv

    ./manage.py load_aff_data CensusPlace per_capita_income GEO.id2 HD01_VD01 HD02_VD01 data/ACS_10_5YR_B19301_with_ann__per_capita_income__places.csv

Aggregate census data to Chicago Community Areas
------------------------------------------------

::

    ./manage.py aggregate_census_fields


Identify suburbs
----------------

::

    ./manage.py flag_chicago_msa_places data/tl_2010_17_place10_chicago_msa.csv


Identify suburbs in Cook County
-------------------------------

::

    ./manage.py flag_cook_county_places


Load raw dispositions data
--------------------------

This command will also fix known issues with columbs being shifted in some rows due to bad escaping of quoted columns in the raw CSV file.

Note that the ``--delete`` flag removes any previous records.

::

    ./manage.py load_dispositions_csv --delete data/Criminal_Convictions_ALLCOOK_05-09.csv


Populate clean disposition records
----------------------------------

Note that the ``--delete`` flag removes any previous records.

::

    ./manage.py create_dispositions --delete


Geocode disposition records
---------------------------

::

    ./manage.py geocode_dispositions


Detect Community Area and Census Place boundaries
-------------------------------------------------

::

    ./manage.py boundarize


Create convictions records from the dispositions
------------------------------------------------

::

    ./manage.py create_convictions --delete


Export Community Area and Census Place GeoJSON
----------------------------------------------

::

    ./manage.py export_model_geojson CommunityArea > community_areas.json

    ./manage.py export_model_geojson CensusPlace > suburbs.json


Export most common charges overall
----------------------------------

::

    ./manage.py most_common_statutes > top_statutes.csv

Export most common charges by community area
--------------------------------------------

::

    ./manage.py most_common_statutes_by_geo > top_statutes_by_community_area.csv


Extract Chicago and Cook County's border from a shapefile
---------------------------------------------------------

::

    ./manage.py border_geojson_from_shp data/gz_2010_17_160_00_500k/gz_2010_17_160_00_500k.shp data/gz_2010_us_050_00_500k/gz_2010_us_050_00_500k.shp > chicago_cook_borders.json

Export convictions by age bucket
--------------------------------

::

   ./manage.py export_age_json > convictions_by_age.json


Export disposition data
-----------------------

Export Disposition model records to CSV.  Anonymize the data by dropping personal identifier fields and converting address fields to the block.  For example, an address number of "2707" would be converted to "2700".

::

    ./manage.py export_public_data > dispositions.csv


Export table of felony convictions
----------------------------------

Export a CSV table of felony convictions by class and year, mirroring the format of the data at https://performance.cookcountyil.gov/Public-Safety/Number-Of-Felony-Cases-Filed-By-Felony-Class/kcfs-dufb

Export count of cases where there ended up being a felony conviction.  In this case, there may have been a charge that started as a misdemeanor but was later ammended to be a felony.

::

    ./manage.py export_cases_by_class


Export count of cases where there was always a felony charge.  That is, the charges filed were for felonies and they were never ammended to a different type.

::

    ./manage.py export_cases_by_class --filter felony_always


Export table of how charge classes were amended
-----------------------------------------------

::

    ./manage export_cases_class_change

Or, as percentages (which is probably easier for seeing trends) ::

    ./manage export_cases_class_change --pct


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
* `2010 Illinois County TIGER Shapefile <ftp://ftp2.census.gov/geo/pvs/tiger2010st/17_Illinois/17/tl_2010_17_county10.zip>`_
* `2010 Census Cartographic Boundary Shapefile for Counties <https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html>`_
* `2010 Census Cartographic Boundary Shapefile for Places <https://www.census.gov/geo/maps-data/data/cbf/cbf_place.html>`
* 2010 ACS 5-year Estimates "TOTAL POPULATION" (B01003) for Cook County Census Tracts
* 2010 ACS 5-year Estimates "TOTAL POPULATION" (B01003) for Illinois Census Places
* 2010 ACS 5-year Estimates "PER CAPITA INCOME IN THE PAST 12 MONTHS (IN 2010 INFLATION-ADJUSTED DOLLARS)" (B19301) for Cook County Census Tracts
* `2010 ACS 5-year Estimates "PER CAPITA INCOME IN THE PAST 12 MONTHS (IN 2010 INFLATION-ADJUSTED DOLLARS)" (B19301) for Illinois Census Places <http://factfinder2.census.gov/faces/tableservices/jsf/pages/productview.xhtml?pid=ACS_10_5YR_B19301&prodType=table>`_
