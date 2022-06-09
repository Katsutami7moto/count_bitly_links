import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
ACCESS_TOKEN: str = os.getenv('ACCESS_TOKEN')
BEARER = f'Bearer {ACCESS_TOKEN}'
API_URL = 'https://api-ssl.bitly.com/v4/{}'


def requests_get(url: str, get_param: str = '', headers: dict = None, params: dict = None) -> requests.Response:
    response = requests.get(url=url.format(get_param), headers=headers, params=params)
    response.raise_for_status()
    return response


def requests_post(url: str, get_param: str, headers: dict, payload: dict) -> requests.Response:
    response = requests.post(url=url.format(get_param), headers=headers, json=payload)
    response.raise_for_status()
    return response


def retrieve_user_info() -> dict:
    headers = {
        'Authorization': BEARER,
    }
    response = requests_get(API_URL, 'user', headers)
    return response.json()


def shorten_link(link: str, group_guid: str) -> str:
    headers = {
        'Authorization': BEARER,
        'Content-Type': 'application/json',
    }
    payload = {
        'long_url': link,
        'domain': 'bit.ly',
        'group_guid': group_guid,
    }
    requests_get(link)  # wrong long url test
    response = requests_post(API_URL, 'shorten', headers, payload)
    resp_json: dict = response.json()
    bitlink: str = resp_json['link']
    return bitlink


def count_clicks(link: str) -> int:
    headers = {
        'Authorization': BEARER,
    }
    params = {
        'units': '-1'
    }
    parsed = urlparse(link)
    parsed_bitlink = parsed.netloc + parsed.path
    api_method = f'bitlinks/{parsed_bitlink}/clicks/summary'
    response = requests_get(API_URL, api_method, headers, params)
    resp_json: dict = response.json()
    clicks: int = resp_json['total_clicks']
    return clicks


def get_shortened_link(long_url: str, guid: str) -> str:
    bitlink = shorten_link(long_url, guid)
    return f'Bitlink: {bitlink}'


def get_clicks_count(bitlink: str) -> str:
    clicks = count_clicks(bitlink)
    return f'Number of clicks: {clicks}'


def is_bitlink(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.netloc == 'bit.ly'


def get_message(url: str, guid: str) -> str:
    if is_bitlink(url):
        message = get_clicks_count(url)
    else:
        message = get_shortened_link(url, guid)
    return message


def main():
    user_info = retrieve_user_info()
    guid: str = user_info['default_group_guid']
    while True:
        url = input('Enter a link (or just press "Enter" to quit): ')
        if not url:
            break
        try:
            message = get_message(url, guid)
        except requests.exceptions.HTTPError as err:
            print('HTTP error:', err)
            print('It is possible that your link contains a typo.')
        except Exception as e:
            print('Other error:', e)
            print("Please, contact script's author.")
        else:
            print(message)
        finally:
            print()


if __name__ == "__main__":
    main()
