from poleno.pages.sitemaps import PagesSitemap

from .apps.inforequests.sitemaps import InforequestsSitemap, InforequestsPagingSitemap
from .apps.obligees.sitemaps import ObligeesSitemap


sitemaps = {
        u'pages': PagesSitemap,
        u'inforequests': InforequestsSitemap,
        u'inforequests_paging': InforequestsPagingSitemap,
        u'obligees': ObligeesSitemap,
}
