from tqdm import tqdm
import os
import requests
from urllib.parse import unquote


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
