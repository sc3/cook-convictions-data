from .defaults import *

# SECURITY WARNING: keep the secret key used in production secret!
# You need to generate a secret key.  You can do it using this
# python snippet:
#
# from django.utils.crypto import get_random_string
# chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
# get_random_string(50, chars)
SECRET_KEY = "" 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# Settings specific to the convictions project

# For now, we're using the MapQuest Geocoder.  You'll need to sign up
# and get an API KEY at http://developer.mapquest.com.  Copy and paste
# that value into this variable.
CONVICTIONS_GEOCODER_API_KEY = ""
