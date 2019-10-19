from poleno.pages.sitemaps import PagesSitemap

from .apps.inforequests.sitemaps import InforequestsSitemap, PublishedInforequestsSitemap
from .apps.obligees.sitemaps import ObligeesSitemap


sitemaps = {
        u'pages': PagesSitemap,
        u'inforequests': InforequestsSitemap,
        u'published_inforequests': PublishedInforequestsSitemap,
        u'obligees': ObligeesSitemap,
}
