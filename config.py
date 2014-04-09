import os


_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
ASSETS_DEBUG = False

CACHE_TYPE = 'memcached'
CACHE_KEY_PREFIX = 'obstructures_dev'

ADMINS = frozenset(['matteson@obstructures.org'])
SECRET_KEY = 'REPLACEME'