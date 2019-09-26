from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap
from django.db.models import Max

from poleno.utils.urls import reverse
from poleno.utils.translation import translation

from .models import Action, Inforequest


class InforequestsSitemap(Sitemap):
    changefreq = u'weekly'
    priority = 0.5

    def items(self):
        res = []
        inforequests = Inforequest.objects.published()
        for lang, name in settings.LANGUAGES:
            for inforequest in inforequests:
                res.append((lang, inforequest))
        return res

    def location(self, (lang, inforequest)):
        with translation(lang):
            return reverse(u'inforequests:detail', args=[inforequest.slug, inforequest.pk])

    def lastmod(self, (lang, inforequest)):
        return (Action.objects
                .where_inforequest(inforequest)
                .aggregate(most_recent=Max(u'created'))[u'most_recent'])
