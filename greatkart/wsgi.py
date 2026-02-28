import os
# Uncomment this in production server
#import sys
#sys.path.insert(0, '/var/www/html/Brandstore')
#sys.path.insert(0, '/var/www/html/Brandstore/venv')
#sys.path.insert(0, '/var/www/html/Brandstore/greatkart')
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatkart.settings')

application = get_wsgi_application()
