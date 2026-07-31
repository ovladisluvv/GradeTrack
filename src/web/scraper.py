import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, RequestException

from .exceptions import GradesPageLoadError


def scrape_grades(session: requests.Session, grades_url: str) -> str:
    """Access the grades page using an authenticated session and return HTML content"""
    try:
        get_response = session.get(grades_url, timeout=10)
        get_response.raise_for_status()

    except HTTPError as error:
        raise GradesPageLoadError(f"Ошибка HTTP при получении страницы с оценками: {error}") from error

    except RequestException as error:
        raise GradesPageLoadError(f"Ошибка сетевого подключения при получении страницы с оценками: {error}") from error

    soup = BeautifulSoup(get_response.text, "html.parser")

    if soup.select_one("form#login-form"):
        redirect_chain = " -> ".join([response.url for response in get_response.history] + [get_response.url])

        raise GradesPageLoadError(f"Вместо страницы оценок получена страница авторизации. Сессия не была авторизована. Цепочка запросов: {redirect_chain}")

    if not soup.select_one("tr[data-key]"):
        raise GradesPageLoadError("Страница была загружена, но таблица оценок не найдена. Возможно, структура страницы изменилась")

    return get_response.text
