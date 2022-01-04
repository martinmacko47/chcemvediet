from allauth.account.adapter import DefaultAccountAdapter

from poleno.invitations.adapters import InvitationsAdapter


class AccountAdapter(InvitationsAdapter, DefaultAccountAdapter):
    def login(self, request, user):
        if not hasattr(user, u'backend'):
            user.backend = u'chcemvediet.auth_backends.AllauthAuthenticationBackendWithAdminLoginAs'
        return super(AccountAdapter, self).login(request, user)
