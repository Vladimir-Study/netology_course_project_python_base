from pprint import pprint
import requests
import time
from datetime import date, datetime
import os
import json

parameters_dict = {}
with open('app vk.txt', 'r') as f:
    for line in f.readlines():
        parameters_dict[line.strip().split(':')[0]] = line.strip().split(':')[1]


class VkPhotoInYaDisk:
    url = 'https://api.vk.com/method/'

    def __init__(self, ya_token, id_vk):
        self.token_ya = ya_token
        self.id_vk = id_vk
        self.params_vk = {
            'access_token': parameters_dict['token VK'],
            'v': '5.131'
        }
        self.headers_ya = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def _get_url_photo_vk(self):
        photo_download_url = self.url + 'photos.get'
        photo_download_parameters = {
            'owner_id': self.id_vk,
            'album_id': 'profile',
            'extended': 1,
            'count': 50
        }
        req = requests.get(photo_download_url, params={**self.params_vk, **photo_download_parameters})
        return req.json()

    def download_photo_and_create_json(self):
        items = self._get_url_photo_vk()['response']['items']
        name_dir = str(date.today())
        create_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params_create_dir = {
            'path': str(name_dir)
        }
        requests.put(create_dir_url, headers=self.headers_ya, params=params_create_dir)
        write_json = []
        info_name = {}
        for like in items:
            if like['likes']['count'] not in info_name.keys():
                info_name[like['likes']['count']] = 1
            else:
                info_name[like['likes']['count']] += 1
        for item in items:
            name = item['likes']['count']
            date_add = datetime.fromtimestamp(item['date']).strftime('%d-%m-%y %H-%M-%S')
            if info_name[name] > 1:
                name = str(name) + ' ' + str(date_add)
            url_photo_max_size = item['sizes'][-1]['url']
            url_upload_to_ya = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params_upload_to_ya = {
                'path': f'{name_dir}/{str(name)}',
                'url': url_photo_max_size
            }
            requests.post(url_upload_to_ya, headers=self.headers_ya, params=params_upload_to_ya)
            height = item['sizes'][-1]['height']
            width = item['sizes'][-1]['width']
            add_write_json = {
                'file_name': f'{str(name)}.jpg',
                'size': f'{str(height)}x{str(width)}',
            }
            write_json.append(add_write_json)
        with open('foto_info.json', 'w') as file_json:
            json.dump(write_json, file_json, indent=4)


Durov = VkPhotoInYaDisk(parameters_dict['token Ya'], 552934290)
Durov.download_photo_and_create_json()
