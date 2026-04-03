# Uncomment this from ./greatkart/wsgi.py in production server
#import sys
#sys.path.insert(0, '/var/www/html/Brandstore')
#sys.path.insert(0, '/var/www/html/Brandstore/venv')
#sys.path.insert(0, '/var/www/html/Brandstore/greatkart')


'NAME': BASE_DIR / 'db.sqlite3',
#'NAME': '/app/db/db.sqlite3', 
# Uncomment the above line and comment previous line in production server



# Uncomment this in ./greatkart/setting.py Production server
#EMAIL_HOST = '10.3.103.129'
#EMAIL_PORT = 25
#EMAIL_USE_TLS = False

# Uncomment this in ./orders/views.py Production server
#server.starttls()
#server.login(sender_email, sender_password)

# Create db and media folders in the app directory before compiling
