SET DJANGO_SETTINGS_MODULE=%DJANGO_SITENAME%.settings_dev
python manage.py migrate --run-syncdb
python manage.py loaddata sandbox_data"
REM python manage.py loaddata auth sandbox
