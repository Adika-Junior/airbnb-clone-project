"""
Reference WSGI configuration for PythonAnywhere
This is what should be in /var/www/itspjay_pythonanywhere_com_wsgi.py
"""

# This file contains the WSGI configuration required to serve up your
# web application at http://itspjay.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI application of your Django app.

import sys
import os

# Add your project directory to the sys.path
path = '/home/ItsPJay/airbnb-clone-project'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'airbnb_clone.settings'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
