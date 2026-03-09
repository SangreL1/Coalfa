from django.contrib.auth.backends import ModelBackend
from coalfa.models import Usuario


class RutBackend(ModelBackend):
    """Authenticates users using their RUT instead of username."""

    def authenticate(self, request, rut=None, password=None, username=None, **kwargs):
        # Support both 'rut' and 'username' parameters for compatibility with admin
        rut_value = rut or username
        if not rut_value:
            return None

        rut_value = rut_value.upper().replace(".", "").replace(" ", "")

        try:
            user = Usuario.objects.get(rut=rut_value)
        except Usuario.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
