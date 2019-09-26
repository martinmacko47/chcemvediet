from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap

from poleno.utils.urls import reverse
from poleno.utils.translation import translation

from .models import Obligee
from .views import OBLIGEES_PER_PAGE

class ObligeesSitemap(Sitemap):
    changefreq = u'weekly'
    priority = 0.3

    def items(self):
        obligees = Obligee.objects.pending().order_by_name()
        paginator = Paginator(obligees, OBLIGEES_PER_PAGE)
        return [(lang, i) for lang, name in settings.LANGUAGES for i in paginator.page_range]

    def location(self, (lang, i)):
        with translation(lang):
            return u"{}?page={}".format(reverse(u'obligees:index'), i)
