import requests
from requests.exceptions import HTTPError, RequestException
from bs4 import BeautifulSoup


def auth_lk(login_url: str, email: str, password: str) -> requests.Session | None:
    session = requests.Session()

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0 (Edition std-1)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-Ch-Ua': '"Opera GX";v="110", "Chromium";v="124", "Not-A.Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"'
    })

    try:
        get_response = session.get(login_url, timeout=10)
        get_response.raise_for_status()

        soup = BeautifulSoup(get_response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': '_csrf-frontend'})

        if not csrf_input:
            print("Ошибка авторизации: На странице нет поля _csrf-frontend. Структура формы входа могла измениться")
            return None

        csrf_token = csrf_input.get('value')
        login_payload = {
            '_csrf-frontend': csrf_token,
            'LoginForm[email]': email,
            'LoginForm[password]': password
        }

        post_response = session.post(login_url, data=login_payload, timeout=10)
        post_response.raise_for_status()

        if "У нас нет пользователей с такой почтой" in post_response.text:
            print("Ошибка авторизации: Неверный email")
            return None
        elif "Неверный пароль" in post_response.text:
            print("Ошибка авторизации: Неверный пароль")
            return None

        return session

    except HTTPError as http_error:
        print(f"Ошибка HTTP при авторизации: {http_error}")
        return None

    except RequestException as req_error:
        print(f"Ошибка сетевого подключения при авторизации: {req_error}")
        return None
