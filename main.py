import requests
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
        # Работаем дальше
        # pprint((temp['response']['items']['sizes']))
        pprint(self._choose_photo_max_size(temp))
        return response.json()


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Authorization': f'OAuth {self.token}'
        }

    # def _get_upload_url(self, file_name, file_path):
    #     upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    #     headers = self.get_headers()
    #     print(file_name)
    #     print(file_path)
    #     params = {"path": file_name, "overwrite": "true"}
    #     response = requests.get(upload_url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()

    def upload(self, file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        file_name = 'file/500.jpg'
        headers = self.get_headers()
        params = {"path": file_name, "url": file_path, "overwrite": "true"}
        # response_dict = self._get_upload_url(file_name, file_path)
        # upload_files_url = response_dict.get("href", "")
        response = requests.post(upload_url, headers=headers, params=params)
        response.raise_for_status()
        print(response.status_code)
        if response.status_code == 201:
            print('Status: OK')
        # url_file = f'{file_name}'
        #
        # r = requests.get(url_file)
        # print(type(r))
        # with open(fr'{file_name}', 'rb') as file:
        #     response = requests.put(upload_files_url, files={"file": file})
        #     response.raise_for_status()
        #     if response.status_code == 201:
        #         print('Status: OK')
        #
        # with open(r, 'wb') as file:
        #     response = requests.put(upload_files_url, files={"file": file})
        #     response.raise_for_status()
        #     if response.status_code == 201:
        #         print('Status: OK')
        # for file_path in file_list:
        #     response_dict = self._get_upload_url(f'{path_to_dir}/{file_path}')
        #     upload_files_url = response_dict.get("href", "")
        #     with open(f'{path_to_dir}/{file_path}', 'rb') as file:
        #         response = requests.put(upload_files_url, files={"file": file})
        #         response.raise_for_status()
        #         if response.status_code == 201:
        #             print('Status: OK')
        return 'Done'


def get_token_id_from_file(file_name):
    with open(f'{file_name}.txt', "r") as file:
        token_id = file.read()
    return token_id


if __name__ == '__main__':
    access_token = get_token_id_from_file('token')
    user_id = get_token_id_from_file('id')
    ya_token = get_token_id_from_file('yatoken')
    vk = VK(access_token, user_id)
    print(vk.users_info())
    pprint(vk.get_photo())
    # path_to_dir = 'files'
    path_to_file = 'https://sun9-east.userapi.com/sun9-60/s/v1/if2/aLgdB2AbtzK6TLR7R5f_TKo14ZPqicKcJfEGqD-1gxqqR2wo418cH3uaxa5lFs66zszvqW9qGh0ksyXmd_RJRDVY.jpg?size=1536x2048&quality=96&type=album'
    uploader = YaUploader(ya_token)
    result = uploader.upload(path_to_file)
    print(result)
