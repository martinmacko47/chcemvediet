from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_backends

from poleno.invitations.adapters import InvitationsAdapter


backend = get_backends()[0]

class AccountAdapter(InvitationsAdapter, DefaultAccountAdapter):
    def login(self, request, user):
        if not hasattr(user, u'backend'):
            user.backend = u'chcemvediet.auth_backends.AllauthAuthenticationBackendWithAdminLoginAs'
        return super(AccountAdapter, self).login(request, user)
