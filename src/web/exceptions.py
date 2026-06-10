class WebClientError(Exception):
    """Base exception for web client errors"""


class AuthError(WebClientError):
    """Base exception for authorization errors"""


class LoginPageLoadError(AuthError):
    """Raised when login page cannot be loaded"""


class CsrfTokenNotFoundError(AuthError):
    """Raised when CSRF token is missing on the login page"""


class LoginRequestError(AuthError):
    """Raised when login POST request fails"""


class InvalidEmailError(AuthError):
    """Raised when email is invalid"""


class InvalidPasswordError(AuthError):
    """Raised when password is invalid"""


class GradesPageLoadError(WebClientError):
    """Raised when grades page cannot be loaded"""
