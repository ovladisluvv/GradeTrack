import requests
from requests.exceptions import HTTPError, RequestException

from .exceptions import GradesPageLoadError


def scrape_grades(session: requests.Session, grades_url: str) -> str:
    """Access the grades page using the authenticated session and return the HTML content"""
    try:
        get_response = session.get(grades_url, timeout=10)
        get_response.raise_for_status()

    except HTTPError as error:
        raise GradesPageLoadError(f"Ошибка HTTP при получении страницы с оценками: {error}") from error

    except RequestException as error:
        raise GradesPageLoadError(f"Ошибка сетевого подключения при получении страницы с оценками: {error}") from error

    return get_response.text
