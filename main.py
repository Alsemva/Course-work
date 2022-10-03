import requests
import time
from progress.bar import IncrementalBar
from pprint import pprint


class VK:

    def __init__(self, access_token, user_id, version='5.131', album_id='profile', extended_opt='1'):
        self.token = access_token
        self.id = user_id
        self.extended = extended_opt
        self.album_id = album_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        return response.json()

    def _max_size(self, item):
        letters = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        for letter in letters:
            for characteristic in item:
                if letter == characteristic['type']:
                    return characteristic['url']

    def _choose_photo_max_size(self, response):
        """"При совпадении лайков у фото, добавляется +1 лайк"""
        max_photo_size_dict = {}
        for item in response['response']['items']:
            if item['likes']['count'] in max_photo_size_dict:
                item['likes']['count'] += 1
            max_photo_size_dict[item['likes']['count']] = self._max_size(item['sizes'])
        return max_photo_size_dict

    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': self.album_id, 'extended': self.extended}
        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        temp = response.json()
        return self._choose_photo_max_size(temp)


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Authorization': f'OAuth {self.token}'
        }

    def upload(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        url_photo = vk.get_photo()
        headers = self.get_headers()
        bar = IncrementalBar('Countdown', max=len(url_photo))
        # print(len(url_photo))
        # return 'done'
        for file_name, file_path in url_photo.items():
            params = {"path": f"photo/{file_name}.jpg", "url": f"{file_path}", "overwrite": "true"}
            response = requests.post(upload_url, headers=headers, params=params)
            response.raise_for_status()
            # print(response.status_code)
            # if response.status_code == 202:
            #     print('Status: OK')
            bar.next()
            time.sleep(1)
        bar.finish()
        return 'Done'


def get_token_id_from_file(file_name):
    with open(f'{file_name}.txt', "r") as file:
        token_id = file.read()
    return token_id


def get_access():
    get_access_key = {
        'access_token': get_token_id_from_file('token'),
        'user_id': get_token_id_from_file('id'),
        'ya_token': get_token_id_from_file('yatoken')
    }
    return get_access_key


if __name__ == '__main__':
    access_key = get_access()
    # print(access_key)
    vk = VK(access_key['access_token'], access_key['user_id'])
    user = vk.users_info()
    # print(user)
    print(f"User: {user['response'][0]['first_name']} {user['response'][0]['last_name']}")
    uploader = YaUploader(access_key['ya_token'])
    result = uploader.upload()
    print(result)
