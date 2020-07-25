from chcemvediet import settings

from django.apps import AppConfig


class ChcemvedietConfig(AppConfig):
    name = u'chcemvediet.apps'

    def ready(self):
        if settings.DATABASES[u'default'][u'ENGINE'] == u'django.db.backends.sqlite3':
            # Workaround for a bug in `_sqlite_format_dtdelta`.
            #
            # When creating a model instance with a datetime field in sqlite, it is formatted as
            # "2020-07-03 10:46:13.391936" without the timezone suffix. However, when updating an
            # existing model instance by incrementing the datetime field with `timedelta`, the
            # timezone suffix "+00:00" is appended to the result. So the resulting datetime is
            # formatted as "2020-07-03 10:46:13.391936+00:00". Datetime fields in sqlite are
            # represented using strings. Therefore two datetimes one with and one without the
            # timezone suffix compare different even if they represent the same time.
            #
            # The problem is in Django `_sqlite_format_dtdelta` function which returns the datetime
            # sting with the timezone suffix while it should not. We fix it by monkey patching
            # `_sqlite_format_dtdelta` and striping the timezone suffix from its results.
            #
            # The bug seems to be fixed in Django 3.1rc1.
            # See: https://github.com/django/django/commit/88637064b3118f90ae5a402e1b47a243ef88d656

            import django.db.backends.sqlite3.base
            original_sqlite_format_dtdelta = django.db.backends.sqlite3.base._sqlite_format_dtdelta

            def new_sqlite_format_dtdelta(*args):
                res = original_sqlite_format_dtdelta(*args)
                return res.strip(u'+00:00') if res else None

            django.db.backends.sqlite3.base._sqlite_format_dtdelta = new_sqlite_format_dtdelta
