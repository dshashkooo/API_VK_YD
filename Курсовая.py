from pprint import pprint
import json
import os
import requests
from urllib.parse import unquote, urlencode
from tqdm import tqdm


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


class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.199'
        }

    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    def get_profile_photos(self):
        parameters = self.get_common_params()
        parameters.update({
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        })
        response = requests.get(self._build_url('photos.get'),
                                params=parameters)
        return response.json()

    def get_max_photo_size(self):
        # Поиск фотографий с самым большим размером
        info_photos = self.get_profile_photos()
        get_photo = {}
        for photo in info_photos['response']['items']:
            sizes = photo.get('sizes')
            max_size_photo = max(sizes, key=lambda x: x['height'] + x['width'])
            if max_size_photo:
                url = max_size_photo['url']
                filename = url.split('/')[-1].split('?')[0]
                get_photo[f'Likes: {photo["likes"]["count"]}'] = {'filename': filename,
                                                                  'type': max_size_photo['type'],
                                                                  'url': url}
        return get_photo

    def download_json(self):
        get_photo = self.get_max_photo_size()
        with open('file1.json', 'w') as json_file:
            json.dump(get_photo, json_file)


class YD:
    def __init__(self, token):
        self.token = token

    def header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder_in_yd(self):
        # Создание папки Images_VK
        headers = self.header()
        url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
        parameters = {
            'path': 'Images_VK',
            'overwrite': 'true'
        }
        response = requests.put(url=url_create_folder,
                                params=parameters,
                                headers=headers)
        return f'Status code (create folder): {response.status_code}'

    def url_for_download(self, url):
        for url in tqdm(url, desc="Downloading"):
            # Фильтрация неправильных ссылок
            filename = os.path.basename(unquote(url.split('/')[-1]))
            filename = ''.join(c for c in filename if c.isalnum() or c in ['.', '_', '-'])
            url_get_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = self.header()
            response = requests.get(url_get_upload,
                                    headers=headers,
                                    params={'path': f'Images_VK/{filename}'})
            url_for_upload = response.json().get('href')

            # Проверка наличия файла на Yandex Disk
            check_exists_response = requests.get(
                f'https://cloud-api.yandex.net/v1/disk/resources?path=Images_VK/{filename}',
                headers=headers)
            if check_exists_response.status_code == 200:
                print(f"File {filename} already exists. Skipping upload.")
                continue

            # Загрузка файла

            with requests.get(url) as r:
                response = requests.put(url=url_for_upload,
                                        headers=headers, data=r.content)
                print(f"Uploaded {filename}. Status code: {response.status_code}")


if __name__ == '__main__':
    print(get_token())

    vk_token = input('Your VK TOKEN: ')
    id_client = input('Your VK ID: ')
    yd_token = input('Your Yandex Disk TOKEN: ')

    vk_client = VKAPIClient(vk_token, id_client)
    photos_info = vk_client.get_profile_photos()
    max_photo = vk_client.get_max_photo_size()

    pprint(vk_client.download_json())

    yandex = YD(yd_token)
    urls = [photo_info['url'] for photo_info in max_photo.values()]

    pprint(yandex.url_for_download(urls))
