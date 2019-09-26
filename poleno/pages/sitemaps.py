import datetime

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from .pages import Page


class PagesSitemap(Sitemap):
    changefreq = u'weekly'
    priority = 0.7

    def items(self):
        res = []
        for lang, name in settings.LANGUAGES:
            for page in Page(u'/', lang).walk():
                if page.is_disabled or page.is_redirect:
                    continue
                res.append(page)
        return res

    def location(self, page):
        return page.url

    def lastmod(self, page):
        try:
            return datetime.datetime.fromtimestamp(page.mtime)
        except:
            return None
