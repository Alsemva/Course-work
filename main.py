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

    def get_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': self.album_id, 'extended': self.extended}
        response = requests.get(url, params={**self.params, **params})
        response.raise_for_status()
        return response.json()


def get_token_id_from_file(file_name):
    with open(f'{file_name}.txt', "r") as file:
        token_id = file.read()
    return token_id


access_token = get_token_id_from_file('token')
user_id = get_token_id_from_file('id')
vk = VK(access_token, user_id)
print(vk.users_info())
pprint(vk.get_photo())
