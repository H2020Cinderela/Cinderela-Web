#
import os

DB_ACCESSIBILITY_NAME = os.environ.get('DB_ACCESSIBILITY_NAME',
                                       'gdse_accessibility')
DB_ACCESSIBILITY_USER = os.environ.get('DB_ACCESSIBILITY_USER', 'isochrone')
DB_ACCESSIBILITY_PASS = os.environ.get('DB_ACCESSIBILITY_PASS', '')

accessibility_db = {
    'accessibility_db': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': DB_ACCESSIBILITY_NAME,
        'USER': DB_ACCESSIBILITY_USER,
        'PASSWORD': DB_ACCESSIBILITY_PASS,
        'HOST': 'h2020repair.bk.tudelft.nl',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            },
        'TEST': {
            'NAME': 'test_gdse_accessibility',
            'TEMPLATE': 'postgis_template',
                    },
        }
    }


class AccessibilityDatabaseRouter:
    """
    Determine how to route database calls for an app's models
    (in this case, for an app named accessibility).
    All other models will be routed to the next router in the
    DATABASE_ROUTERS setting if applicable,
    or otherwise to the default database.
    """

    def db_for_read(self, model, **hints):
        """Send all read operations
        on Example app models to `accessibility`."""
        if model._meta.app_label == 'accessibility':
            return 'accessibility_db'
        return None

    def db_for_write(self, model, **hints):
        """Send all write operations
        on Example app models to `example_db`."""
        if model._meta.app_label == 'accessibility':
            return 'accessibility_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Determine if relationship is allowed between two objects."""

        # Allow any relation between two models
        # that are both in the Example app.
        if obj1._meta.app_label == 'accessibility' \
           and obj2._meta.app_label == 'accessibility':
            return True
        # No opinion if neither object is in the
        # Example app (defer to default or other routers).
        elif 'accessibility' not in [obj1._meta.app_label,
                                     obj2._meta.app_label]:
            return None

        # Block relationship if one object is
        # in the Example app and the other isn't.
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that the Example app's
        models get created on the right database."""
        if app_label == 'accessibility':
            # The Example app should be migrated
            # only on the example_db database.
            return db == 'accessibility_db'
        elif db == 'accessibility_db':
            # Ensure that all other apps don't get migrated
            # on the example_db database.
            return False
        # No opinion for all other scenarios
        return None
