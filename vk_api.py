import requests


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
            'user_ids': self.user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        })
        response = requests.get(self._build_url('photos.get'),
                                params=parameters)
        return response.json()

    def get_max_photo_size(self, count_photos):
        # Поиск фотографий с самым большим размером
        info_photos = self.get_profile_photos()
        get_photo = {}
        counter: int = 0
        for photo in info_photos['response']['items']:
            sizes = photo.get('sizes')
            max_size_photo = max(sizes, key=lambda x: x['height'] + x['width'])
            if max_size_photo:
                url = max_size_photo['url']
                filename = url.split('/')[-1].split('?')[0]
                date = photo["date"]
                get_photo[f'Likes: {photo["likes"]["count"], f'Date: {date}'}'] = {'filename': filename,
                                                                                   'type': max_size_photo['type'],
                                                                                   'url': url}
                counter += 1
            if counter == count_photos:
                break

        return get_photo
