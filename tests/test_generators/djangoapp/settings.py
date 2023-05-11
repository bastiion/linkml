from pathlib import Path

import django
from django.conf import settings


def pre_test_stage(app_name):
    if not settings.configured:
        pytest_configure(app_name)
        # django migrate
        django.setup()
        from django.core.management import call_command
        call_command('migrate', verbosity=1, interactive=False)
        # fix for: sqlite3.OperationalError: no such table: animal_animal
        call_command('makemigrations', verbosity=1, interactive=False)
        call_command('makemigrations', app_name, verbosity=1, interactive=False)


BASE_DIR = Path(__file__).resolve().parent.parent


def pytest_configure(app_name):
    settings.configure(
        DEBUG=True,
        ALLOWED_HOSTS=[],
        INSTALLED_APPS=[app_name],
        WSGI_APPLICATION='minimal.wsgi.application',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'output' / 'db.sqlite3',
            }
        },
        LANGUAGE_CODE='en-us',
        TIME_ZONE='UTC',
        USE_I18N=True,
        USE_TZ=True,
        STATIC_URL='static/',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )
