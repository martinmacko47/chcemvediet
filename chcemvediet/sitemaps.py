from django.contrib.sitemaps import Sitemap

from poleno.pages.sitemaps import PagesSitemap

from .apps.inforequests.sitemaps import InforequestSitemap


class HomepageSitemap(Sitemap):
    priority = 1.0
    changefreq = u'never'

    def items(self):
        return [u'homepage']

    def location(self, item):
        return u'/'

sitemaps = {
        u'homepage': HomepageSitemap,
        u'pages': PagesSitemap,
        u'inforequests': InforequestSitemap,
        }
