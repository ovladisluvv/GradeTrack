import requests
from requests.exceptions import HTTPError, RequestException
from bs4 import BeautifulSoup

from .exceptions import (
    LoginPageLoadError,
    CsrfTokenNotFoundError,
    LoginRequestError,
    InvalidEmailError,
    InvalidPasswordError
)


def auth_lk(login_url: str, email: str, password: str) -> requests.Session:
    """Log in to the personal account on the website using given credentials and return an authenticated session"""
    session = requests.Session()

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-Ch-Ua': '"Chromium";v="124", "Not-A.Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"'
    })

    try:
        get_response = session.get(login_url, timeout=10)
        get_response.raise_for_status()

    except HTTPError as error:
        raise LoginPageLoadError(f"Ошибка HTTP при загрузке страницы авторизации: {error}") from error

    except RequestException as error:
        raise LoginPageLoadError(f"Ошибка сетевого подключения при загрузке страницы авторизации: {error}") from error

    soup = BeautifulSoup(get_response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': '_csrf-frontend'})

    if not csrf_input:
        raise CsrfTokenNotFoundError("На странице нет поля _csrf-frontend. Структура формы входа могла измениться")

    csrf_token = csrf_input.get('value')

    if not csrf_token:
        raise CsrfTokenNotFoundError("Поле _csrf-frontend найдено, но не содержит значения")

    login_payload = {
        '_csrf-frontend': csrf_token,
        'LoginForm[email]': email,
        'LoginForm[password]': password,
        "LoginForm[rememberMe]": "1"
    }

    try:
        post_response = session.post(login_url, data=login_payload, timeout=10)
        post_response.raise_for_status()
        post_soup = BeautifulSoup(post_response.text, "html.parser")
        login_form = post_soup.select_one("form#login-form")

        if login_form:
            errors = [
                element.get_text(" ", strip=True)
                for element in post_soup.select("#login-form .help-block-error")
                if element.get_text(strip=True)
            ]

            details = "; ".join(errors)

            if not details:
                details = ("Сайт повторно вернул страницу входа. Проверьте email, пароль и изменения формы авторизации")

            raise LoginRequestError(
                f"Авторизация не выполнена: {details}"
            )

        return session

    except HTTPError as error:
        raise LoginRequestError(f"Ошибка HTTP при отправке запроса авторизации: {error}") from error

    except RequestException as error:
        raise LoginRequestError(f"Ошибка сетевого подключения при отправке запроса авторизации: {error}") from error
