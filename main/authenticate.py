from django.contrib.auth.backends import ModelBackend
from .models import User 

class EmailBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        if email is not None:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
        return None