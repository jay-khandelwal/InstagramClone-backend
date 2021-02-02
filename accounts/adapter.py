from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site

from django.conf import settings

class CustomAdapter(DefaultAccountAdapter):
    
    def get_email_confirmation_url(self, emailconfirmation, current_site):
        url = current_site.domain + '/accounts/confirm-email/' + emailconfirmation.key
        return url
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(emailconfirmation, current_site)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

   