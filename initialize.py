import secrets, argparse, django, os
from pathlib import Path
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings
BASE_DIR = Path(__file__).resolve().parent

def write_settings(node_ip, lnd_dir_path, lnd_network, lnd_rpc_server, whitenoise, debug):
    #Generate a unique secret to be used for your django site
    secret = secrets.token_urlsafe(64)
    if whitenoise:
        wnl = """
    'whitenoise.middleware.WhiteNoiseMiddleware',"""
    else:
        wnl = ''
    settings_file = '''"""
Django settings for lndg project.

Generated by 'django-admin startproject' using Django {{ django_version }}.

For more information on this file, see
https://docs.djangoproject.com/en/{{ docs_version }}/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/{{ docs_version }}/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = %s

ALLOWED_HOSTS = ['%s']

LND_DIR_PATH = '%s'
LND_NETWORK = '%s'
LND_RPC_SERVER = '%s'

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'gui',
    'rest_framework',
    'qr_code',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',%s
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lndg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lndg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/{{ docs_version }}/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/{{ docs_version }}/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'gui/static/')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''' % (secret, debug, node_ip, lnd_dir_path, lnd_network, lnd_rpc_server, wnl)
    try:
        f = open("lndg/settings.py", "x")
        f.close()
    except:
        print('A settings file may already exist, please double check.')
        return
    try:
        f = open("lndg/settings.py", "w")
        f.write(settings_file)
        f.close()
    except Exception as e:
        print('Error creating the settings file:', e)

def write_supervisord_settings(sduser):
    supervisord_secret = secrets.token_urlsafe(16)
    supervisord_settings_file = '''[supervisord]
user=%s
childlogdir = /var/log
logfile = /var/log/supervisord.log
logfile_maxbytes = 50MB
logfile_backups = 30
loglevel = info
pidfile = /var/supervisord.pid
umask = 022
nodaemon = false
nocleanup = false

[inet_http_server]
port = 9001
username = lndg-supervisord
password = %s

[supervisorctl]
serverurl = http://localhost:9001
username = lndg-supervisord
password = %s

[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface

[program:jobs]
command = sh -c "python jobs.py && sleep 15"
process_name = lndg-jobs
directory = %s
autorestart = true
redirect_stderr = true
stdout_logfile = /var/log/lndg-jobs.log
stdout_logfile_maxbytes = 150MB
stdout_logfile_backups = 15

[program:rebalancer]
command = sh -c "python rebalancer.py && sleep 15"
process_name = lndg-rebalancer
directory = %s
autorestart = true
redirect_stderr = true
stdout_logfile = /var/log/lndg-rebalancer.log
stdout_logfile_maxbytes = 150MB
stdout_logfile_backups = 15

[program:htlc-stream]
command = sh -c "python htlc_stream.py && sleep 15"
process_name = lndg-htlc-stream
directory = %s
autorestart = true
redirect_stderr = true
stdout_logfile = /var/log/lndg-htlc-stream.log
stdout_logfile_maxbytes = 150MB
stdout_logfile_backups = 15
''' % (sduser, supervisord_secret, supervisord_secret, BASE_DIR, BASE_DIR, BASE_DIR)
    try:
        f = open("/usr/local/etc/supervisord.conf", "x")
        f.close()
    except:
        print('A supervisord settings file may already exist, please double check.')
        return
    try:
        f = open("/usr/local/etc/supervisord.conf", "w")
        f.write(supervisord_settings_file)
        f.close()
    except Exception as e:
        print('Error creating the settings file:', str(e))

def main():
    help_msg = "LNDg Settings Initializer"
    parser = argparse.ArgumentParser(description = help_msg)
    parser.add_argument('-ip', '--nodeip',help = 'IP that will be used to access the LNDg page', default='*')
    parser.add_argument('-dir', '--lnddir',help = 'LND Directory for tls cert and admin macaroon paths', default='~/.lnd')
    parser.add_argument('-net', '--network', help = 'Network LND will run over', default='mainnet')
    parser.add_argument('-server', '--rpcserver', help = 'Server address to use for rpc communications with LND', default='localhost:10009')
    parser.add_argument('-sd', '--supervisord', help = 'Setup supervisord to run jobs/rebalancer background processes', action='store_true')
    parser.add_argument('-sdu', '--sduser', help = 'Configure supervisord with a non-root user', default='root')
    parser.add_argument('-wn', '--whitenoise', help = 'Add whitenoise middleware (docker requirement for static files)', action='store_true')
    parser.add_argument('-d', '--docker', help = 'Single option for docker container setup (supervisord + whitenoise)', action='store_true')
    parser.add_argument('-dx', '--debug', help = 'Setup the django site in debug mode', action='store_true')
    parser.add_argument('-pw', '--adminpw', help = 'Setup a custom admin password', default=None)
    args = parser.parse_args()
    node_ip = args.nodeip
    lnd_dir_path = args.lnddir
    lnd_network = args.network
    lnd_rpc_server = args.rpcserver
    setup_supervisord = args.supervisord
    sduser = args.sduser
    whitenoise = args.whitenoise
    docker = args.docker
    debug = args.debug
    adminpw = args.adminpw
    if docker:
        setup_supervisord = True
        whitenoise = True
    write_settings(node_ip, lnd_dir_path, lnd_network, lnd_rpc_server, whitenoise, debug)
    if setup_supervisord:
        print('Supervisord setup requested...')
        write_supervisord_settings(sduser)
    try:
        settings.configure(
            SECRET_KEY = secrets.token_urlsafe(64),
            DATABASES = {
                'default':{
                    'ENGINE':'django.db.backends.sqlite3',
                    'NAME':BASE_DIR/'db.sqlite3'
                }
            },
            INSTALLED_APPS = [
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.admin',
                'gui',
            ],
            STATIC_URL = 'static/', 
            STATIC_ROOT = os.path.join(BASE_DIR, 'gui/static/')
        )
        django.setup()
        call_command('migrate', verbosity=0)
        call_command('collectstatic', verbosity=0, interactive=False)
        try:
            call_command('createsuperuser', username='lndg-admin', email='admin@lndg.local', interactive=False)
            admin = get_user_model().objects.get(username='lndg-admin')
            login_pw = secrets.token_urlsafe(16) if adminpw is None else adminpw
            admin.set_password(login_pw)
            admin.save()
            try:
                f = open("lndg-admin.txt", "w")
                f.write(login_pw)
                f.close()
            except Exception as e:
                print('Error writing password file:', str(e))
            print('FIRST TIME LOGIN PASSWORD: ' + login_pw)
        except:
            print('User already created, skipping...')
    except Exception as e:
        print('Error initializing django: ', str(e))

if __name__ == '__main__':
    main()