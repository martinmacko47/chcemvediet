from poleno.pages.sitemaps import PagesSitemap

from .apps.inforequests.sitemaps import InforequestsSitemap
from .apps.obligees.sitemaps import ObligeesSitemap


sitemaps = {
        u'pages': PagesSitemap,
        u'inforequests': InforequestsSitemap,
        u'obligees': ObligeesSitemap,
}
