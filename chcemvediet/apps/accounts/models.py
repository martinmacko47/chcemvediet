# vim: expandtab
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'))
    street = models.CharField(max_length=255, verbose_name=_('Street'))
    city = models.CharField(max_length=255, verbose_name=_('City'))
    zip = models.CharField(max_length=10, verbose_name=_('Zip'))

@receiver(post_save, sender=User)
def create_profile_on_user_post_save(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        profile = Profile(user=user)
        profile.save()
