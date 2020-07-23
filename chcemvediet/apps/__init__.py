from chcemvediet import settings

from django.apps import AppConfig


class ChcemvedietConfig(AppConfig):
    name = u'chcemvediet.apps'

    def ready(self):
        if settings.DATABASES[u'default'][u'ENGINE'] == u'django.db.backends.sqlite3':
            import django.db.backends.sqlite3.base
            original_sqlite_format_dtdelta = django.db.backends.sqlite3.base._sqlite_format_dtdelta

            # Workaround for bug in _sqlite_format_dtdelta:
            # By creating model instance, datetime field in sqlite will be formatted without
            # timezone as "%Y-%m-%d" or "%Y-%m-%d %H:%M:%S[.%f]. By updating model instance,
            # datetime field will be formatted with timezone suffix. Two equal datetimes can differ,
            # because sqlite compares datetimes as strings.
            # Fixed in django 3.1rc1.
            def new_sqlite_format_dtdelta(*args):
                res = original_sqlite_format_dtdelta(*args)
                return res.strip(u'+00:00') if res else None
            django.db.backends.sqlite3.base._sqlite_format_dtdelta = new_sqlite_format_dtdelta
