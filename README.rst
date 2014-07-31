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
---------------------------------

::

    ./manage.py create_dispositions

Geocode disposition records
--------------------------

::

    ./manage.py geocode_dispositions


Other datasets
==============

* `Boundaries - Community Areas (current) <https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6>`_ 
* `Cook County Municipalities <https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Municipality/ta8t-zebk>`_
* `Boundaries - Census Tracts - 2010 <https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Census-Tracts-2010/5jrd-6zik>`_
