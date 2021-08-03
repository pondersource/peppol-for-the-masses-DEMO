from accounts.models import Activation
from django.db.models import Q


class AuthBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False


    def get_user(self, user_id):
       try:
          return UserProfile.objects.get(pk=user_id)
       except UserProfile.DoesNotExist:
          return None


    def authenticate(self, domain_name, password):
        try:
            user = UserProfile.objects.get(
                Q(domain_name=domain_name)
            )
        except UserProfile.DoesNotExist:
            return None

        return user if user.check_password(password) else None
