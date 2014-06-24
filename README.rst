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

Load raw convictions data
-------------------------

::

    ./manage.py load_convictions_csv data/Criminal_Convictions_ALLCOOK_05-09.csv


Populate clean conviction records
---------------------------------

::

    ./manage.py create_convictions

Geocode conviction records
--------------------------

::

    ./manage.py geocode_convictions
