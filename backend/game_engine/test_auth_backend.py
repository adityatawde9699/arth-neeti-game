from rest_framework import authentication
from django.contrib.auth import get_user_model

User = get_user_model()

class TestAuthentication(authentication.BaseAuthentication):
    """
    Simple authentication for testing/dev purposes.
    Allows bypassing auth by setting a specific header or just returns None.
    """
    def authenticate(self, request):
        return None
