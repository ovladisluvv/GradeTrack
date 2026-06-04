import requests
from requests.exceptions import HTTPError, RequestException


def scrape_grades(session: requests.Session, grades_url: str) -> str | None:
    """Access the grades page using the authenticated session and return the HTML content"""
    try:
        get_response = session.get(grades_url, timeout=10)
        get_response.raise_for_status()

        return get_response.text

    except HTTPError as http_error:
        print(f"Ошибка HTTP при получении оценок: {http_error}")
        return None

    except RequestException as req_error:
        print(f"Ошибка сетевого подключения при получении оценок: {req_error}")
        return None
