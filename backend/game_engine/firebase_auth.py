"""
Firebase Authentication for Django
Provides middleware and DRF authentication class for Firebase ID token verification.
"""
import os
import json
import firebase_admin
from pathlib import Path
from firebase_admin import auth, credentials
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from rest_framework import authentication, exceptions

User = get_user_model()


def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Called from apps.py on Django startup.
    """
    if firebase_admin._apps:
        # Already initialized (happens during Django reload)
        return

    # Try loading from JSON string (for production deployment)
    service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON', '')
    if service_account_json:
        try:
            service_account_info = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            print("[SUCCESS] Firebase initialized successfully from JSON env variable")
            return
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
    
    # Try loading from file path (for local development)
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', '')
    print(f"DEBUG: Checking FIREBASE_SERVICE_ACCOUNT_PATH: '{service_account_path}'")
    
    if service_account_path:
        # Resolve path relative to BASE_DIR if it's not absolute
        from django.conf import settings
        path_obj = Path(service_account_path)
        if not path_obj.is_absolute():
            resolved_path = (settings.BASE_DIR / service_account_path).resolve()
            print(f"DEBUG: Resolved relative path to: '{resolved_path}'")
        else:
            resolved_path = path_obj
            print(f"DEBUG: Using absolute path: '{resolved_path}'")

        if resolved_path.exists():
            cred = credentials.Certificate(str(resolved_path))
            firebase_admin.initialize_app(cred)
            print(f"[SUCCESS] Firebase initialized successfully from file: {resolved_path}")
            return
        else:
            print(f"[ERROR] Service account file not found at: {resolved_path}")
    
    print("[WARNING] Firebase not initialized. Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON")


def get_firebase_user(id_token):
    """
    Verify Firebase ID token and return the decoded token.
    
    Args:
        id_token (str): Firebase ID token from client
        
    Returns:
        dict: Decoded token with user info (uid, email, etc.)
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {str(e)}")


def get_or_create_user_from_firebase(firebase_user):
    """
    Get or create Django user from Firebase user data.
    
    Args:
        firebase_user (dict): Decoded Firebase token
        
    Returns:
        User: Django user instance
    """
    uid = firebase_user.get('uid')
    email = firebase_user.get('email', '')
    
    # Try to find user by Firebase UID (stored as username)
    user, created = User.objects.get_or_create(
        username=uid,
        defaults={
            'email': email,
        }
    )
    
    # Update email if it changed
    if not created and user.email != email:
        user.email = email
        user.save()
    
    return user


class FirebaseAuthMiddleware:
    """
    Django middleware to authenticate users via Firebase ID token.
    Extracts token from Authorization header and sets request.user.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split('Bearer ')[1]
            
            try:
                # Verify Firebase token
                firebase_user = get_firebase_user(id_token)
                
                # Get or create Django user
                user = get_or_create_user_from_firebase(firebase_user)
                
                # Set user on request (lazy to avoid multiple DB queries)
                request.user = SimpleLazyObject(lambda: user)
                
            except ValueError as e:
                # Invalid token - let request proceed without auth
                # (will be caught by permission classes if needed)
                pass
        
        response = self.get_response(request)
        return response


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class for Firebase ID tokens.
    Use with @authentication_classes([FirebaseAuthentication]) on API views.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Firebase ID token.
        
        Returns:
            tuple: (user, None) if authenticated
            None: if not authenticated
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        id_token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify Firebase token
            firebase_user = get_firebase_user(id_token)
            
            # Get or create Django user
            user = get_or_create_user_from_firebase(firebase_user)
            
            return (user, None)
            
        except ValueError as e:
            raise exceptions.AuthenticationFailed(f'Invalid Firebase token: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return the authentication scheme (for 401 responses).
        """
        return 'Bearer'
