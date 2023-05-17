import importlib
import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

wsgi = importlib.load_source('wsgi', 'app.py')
application = wsgi.app
