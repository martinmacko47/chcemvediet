from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sitemaps import Sitemap
from django.db.models import Max
from django.utils import translation

from .models import Action, Inforequest


class InforequestSitemap(Sitemap):
    i18n = True
    changefreq = u'weekly'
    priority = 0.5

    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr

    def items(self):
        return Inforequest.objects.published()

    def get_urls(self, page=1, site=None, protocol=None):
        # Determine protocol
        if self.protocol is not None:
            protocol = self.protocol
        if protocol is None:
            protocol = u'http'

        # Determine domain
        if site is None:
            if django_apps.is_installed(u'django.contrib.sites'):
                Site = django_apps.get_model(u'sites.Site')
                try:
                    site = Site.objects.get_current()
                except Site.DoesNotExist:
                    pass
            if site is None:
                raise ImproperlyConfigured(
                    u"To use sitemaps, either enable the sites framework or pass "
                    u"a Site/RequestSite object in your view."
                )
        domain = site.domain

        if getattr(self, u'i18n', False):
            urls = []
            current_lang_code = translation.get_language()
            for lang_code, lang_name in settings.LANGUAGES:
                translation.activate(lang_code)
                urls += self._urls(page, protocol, domain)
            translation.activate(current_lang_code)
        else:
            urls = self._urls(page, protocol, domain)

        return urls

    def _urls(self, page, protocol, domain):
        urls = []
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod
        for item in self.paginator.page(page).object_list:
            loc = u"%s://%s%s" % (protocol, domain, self.__get(u'location', item))
            priority = self.__get(u'priority', item)
            lastmod = self.__get(u'lastmod', item)
            if all_items_lastmod:
                all_items_lastmod = lastmod is not None
                if (all_items_lastmod and
                        (latest_lastmod is None or lastmod > latest_lastmod)):
                    latest_lastmod = lastmod
            url_info = {
                u'item': item,
                u'location': loc,
                u'lastmod': lastmod,
                u'changefreq': self.__get(u'changefreq', item),
                u'priority': str(priority if priority is not None else ''),
            }
            urls.append(url_info)
        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod
        return urls

    def lastmod(self, inforequest):
        return (Action.objects
                .filter(branch__inforequest=inforequest)
                .aggregate(most_recent=Max(u'created'))[u'most_recent'])
