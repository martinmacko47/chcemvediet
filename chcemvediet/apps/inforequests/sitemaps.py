from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap
from django.db.models import Max
from django.utils.http import urlencode

from poleno.utils.urls import reverse
from poleno.utils.translation import translation

from .constants import INFOREQUESTS_PER_PAGE
from .models import Action, Inforequest


class InforequestsSitemap(Sitemap):
    changefreq = u'weekly'
    priority = 0.5

    def items(self):
        inforequests = Inforequest.objects.published()
        return [(lang, inforequest) for lang, name in settings.LANGUAGES
                for inforequest in inforequests]

    def location(self, (lang, inforequest)):
        with translation(lang):
            return reverse(u'inforequests:detail', args=[inforequest.slug, inforequest.pk])

    def lastmod(self, (lang, inforequest)):
        return (Action.objects
                .of_inforequest(inforequest)
                .aggregate(most_recent=Max(u'created'))[u'most_recent'])

class PublishedInforequestsSitemap(Sitemap):
    changefreq = u'weekly'
    priority = 0.3

    def items(self):
        published_inforequests = Inforequest.objects.published()
        paginator = Paginator(published_inforequests, INFOREQUESTS_PER_PAGE)
        return [(lang, i) for lang, name in settings.LANGUAGES for i in paginator.page_range]

    def location(self, (lang, i)):
        with translation(lang):
            return reverse(u'inforequests:index') + u'?' + urlencode({u'page': i})
