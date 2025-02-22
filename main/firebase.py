import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from typing import Dict, Optional
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

class FirebaseError(Exception):
    """Custom exception for Firebase-related errors"""
    pass

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            if os.path.exists(settings.FIREBASE_CERT_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CERT_PATH)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully")
            else:
                error_msg = f"Firebase credentials file not found at {settings.FIREBASE_CERT_PATH}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
    except Exception as e:
        logger.error(f"Firebase initialization error: {str(e)}")
        raise FirebaseError(f"Firebase initialization failed: {str(e)}")

def verify_firebase_token(id_token: str) -> Dict:
    """
    Verify Firebase ID token and return user information
    
    Args:
        id_token (str): Firebase ID token to verify
        
    Returns:
        dict: Decoded token containing user information
        
    Raises:
        AuthenticationFailed: If token is invalid or expired
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        return 'Invalid ID token'
    except auth.ExpiredIdTokenError:
        raise AuthenticationFailed('Expired ID token')
    except auth.RevokedIdTokenError:
        raise AuthenticationFailed('Revoked ID token')
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise AuthenticationFailed('Token verification failed')

def get_user_by_email(email: str) -> Optional[auth.UserRecord]:
    """
    Get Firebase user by email
    
    Args:
        email (str): User's email address
        
    Returns:
        UserRecord: Firebase user record if found, None otherwise
    """
    try:
        return auth.get_user_by_email(email)
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        raise FirebaseError(f"Failed to get user: {str(e)}")

def create_firebase_user(email: str, password: str, display_name: Optional[str] = None) -> auth.UserRecord:
    """
    Create a new Firebase user
    
    Args:
        email (str): User's email address
        password (str): User's password
        display_name (str, optional): User's display name
        
    Returns:
        UserRecord: Created Firebase user record
        
    Raises:
        ValidationError: If user creation fails
    """
    try:
        user_properties = {
            'email': email,
            'password': password,
            'email_verified': False,
        }
        if display_name:
            user_properties['display_name'] = display_name

        user = auth.create_user(**user_properties)
        logger.info(f"Successfully created Firebase user: {user.uid}")
        return user
    except auth.EmailAlreadyExistsError:
        raise ValidationError('Email already exists')
    except Exception as e:
        logger.error(f"User creation error: {str(e)}")
        raise ValidationError(f'Failed to create user: {str(e)}')

def update_firebase_user(uid: str, **kwargs) -> auth.UserRecord:
    """
    Update Firebase user properties
    
    Args:
        uid (str): Firebase user ID
        **kwargs: User properties to update
        
    Returns:
        UserRecord: Updated Firebase user record
    """
    try:
        user = auth.update_user(uid, **kwargs)
        logger.info(f"Successfully updated Firebase user: {uid}")
        return user
    except auth.UserNotFoundError:
        raise ValidationError('User not found')
    except Exception as e:
        logger.error(f"User update error: {str(e)}")
        raise FirebaseError(f'Failed to update user: {str(e)}')

def delete_firebase_user(uid: str) -> None:
    """
    Delete a Firebase user
    
    Args:
        uid (str): Firebase user ID to delete
    """
    try:
        auth.delete_user(uid)
        logger.info(f"Successfully deleted Firebase user: {uid}")
    except auth.UserNotFoundError:
        raise ValidationError('User not found')
    except Exception as e:
        logger.error(f"User deletion error: {str(e)}")
        raise FirebaseError(f'Failed to delete user: {str(e)}')

def disable_firebase_user(uid: str) -> auth.UserRecord:
    """
    Disable a Firebase user account
    
    Args:
        uid (str): Firebase user ID to disable
        
    Returns:
        UserRecord: Updated Firebase user record
    """
    try:
        return auth.update_user(uid, disabled=True)
    except auth.UserNotFoundError:
        raise ValidationError('User not found')
    except Exception as e:
        logger.error(f"User disable error: {str(e)}")
        raise FirebaseError(f'Failed to disable user: {str(e)}')

def send_password_reset_email(email: str) -> None:
    """
    Generate password reset link and send email
    
    Args:
        email (str): User's email address
    """
    try:
        link = auth.generate_password_reset_link(email)
        # Here you would typically send the link via your email service
        logger.info(f"Generated password reset link for: {email}")
        return link
    except auth.UserNotFoundError:
        raise ValidationError('User not found')
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise FirebaseError(f'Failed to generate password reset link: {str(e)}')
    