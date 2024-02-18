from pprint import pprint
from urllib.parse import urlencode
from decouple import config
import json
import vk_api as vk
import ya_api as ya


def token_vk():
    VK_TOKEN = config('vk_token')
    return VK_TOKEN


def token_ya():
    YA_TOKEN = config('ya_token')
    return YA_TOKEN


def get_token():
    APP_ID = "51846243"
    OAUTH_BASE_URL = "https://oauth.vk.com/authorize"
    params = {
        'client_id': APP_ID,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'scope': 'status,photos',
        'response_type': 'token',
    }
    oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
    return oauth_url


def download_json(info_photos):
    with open('file1.json', 'w') as json_file:
        json.dump(info_photos, json_file)


if __name__ == '__main__':
    pprint(get_token())

    id_client = input('Your VK ID (Enter: 123456789 or screen_name): ')

    vk_token = token_vk()
    vk_client = vk.VKAPIClient(vk_token, id_client)
    photos_info = vk_client.get_profile_photos()

    photos = vk_client.get_max_photo_size(5)
    pprint(photos)

    yd_token = token_ya()
    yandex = ya.YD(yd_token)
    urls = [photo_info['url'] for photo_info in photos.values()]

    pprint(yandex.url_for_download(urls))
