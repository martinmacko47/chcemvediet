from captcha.fields import ReCaptchaField
from allauth.account.forms import ResetPasswordForm as AllauthResetPasswordForm


class ResetPasswordForm(AllauthResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields[u'recaptcha'] = ReCaptchaField(label=u'')
