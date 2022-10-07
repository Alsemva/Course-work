import requests
import time
from tqdm import tqdm
import json
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

    def _max_size(self, item, name):
        letters = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        for letter in letters:
            for characteristic in item:
                if letter == characteristic['type']:
                    return {'size': characteristic['type'], 'name': name, 'url': characteristic['url']}

    def _choose_photo_max_size(self, response):
        max_photo_size_list = []
        for item in response['response']['items']:
            max_photo_size_list.append(self._max_size(item['sizes'], item['likes']['count']))
        return max_photo_size_list

    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': self.album_id, 'extended': self.extended}
        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        temp = response.json()
        return self._choose_photo_max_size(temp)


class YaUploader:
    def __init__(self, token: str, number_of_photos):
        self.token = token
        self.upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.number_of_photos = number_of_photos

    def get_headers(self):
        return {
            'Authorization': f'OAuth {self.token}'
        }

    def mk_dir(self, path):
        """creating a directory on yandex.disk"""
        mk_dir_url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = path
        headers = self.get_headers()
        response = requests.get(mk_dir_url, headers=headers, params=params)
        if response.status_code != 200:
            print("Directory created")
            response = requests.put(mk_dir_url, headers=headers, params=params)
        else:
            print("Directory exists")
        return response

    def _get_upload_url(self, path):
        params = {"path": f'{path["path"]}/info.json', "overwrite": "true"}
        headers = self.get_headers()
        response = requests.get(self.upload_url, headers=headers, params=params)
        return response.json()

    def mk_json_file(self, file_data_with_url):
        file_data_without_url = []
        for i in range(0, self.number_of_photos):
            file_data_without_url.append({"file_name": f'{file_data_with_url[i]["name"]}.jpg',
                                          "size": file_data_with_url[i]["size"]})
        file = open("info.json", "w")
        json.dump(file_data_without_url, file, ensure_ascii=False, indent=2)
        file.close()

    def upload_json_file(self, path, file_data_with_url):
        self.mk_json_file(file_data_with_url)
        response_dict = self._get_upload_url(path)
        upload_file_url = response_dict.get("href", "")
        with open("info.json", 'rb') as upload_file:
            response = requests.put(upload_file_url, files={"file": upload_file})
            response.raise_for_status()
            if response.status_code == 201:
                print('\r\nJson file created')

        return response.json

    def upload(self, id_user):
        """Uploading files to yandex.disk"""
        url_photo = vk.get_photo()
        headers = self.get_headers()
        path = {"path": f"photo_{id_user}"}
        self.mk_dir(path).raise_for_status()
        self.upload_json_file(path, url_photo)
        for i in tqdm(range(0, self.number_of_photos)):
            params = {"path": f"{path['path']}/{url_photo[i]['name']}.jpg", "url": f"{url_photo[i]['url']}"}
            response = requests.post(self.upload_url, headers=headers, params=params)
            response.raise_for_status()
            time.sleep(1)
        return '\n Done'


def get_token_id_from_file(file_name):
    with open(f'{file_name}.txt', "r") as file:
        token_id = file.read()
    return token_id


def get_access():
    get_access_key = {
        'access_token': get_token_id_from_file('token'),
        'user_id': get_token_id_from_file('id'),
        'ya_token': get_token_id_from_file('yatoken'),
        'number_of_photos': 5
    }
    return get_access_key


if __name__ == '__main__':
    access_key = get_access()
    vk = VK(access_key['access_token'], access_key['user_id'])
    user = vk.users_info()
    print(f"User: {user['response'][0]['first_name']} {user['response'][0]['last_name']}")
    uploader = YaUploader(access_key['ya_token'], access_key['number_of_photos'])
    result = uploader.upload(access_key['user_id'])
    print(result)
