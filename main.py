from pprint import pprint
import requests
from datetime import date, datetime
import json
import time
from tqdm import tqdm
from hashlib import md5

parameters_dict = {}
with open('app vk.txt', 'r') as f:
    for line in f.readlines():
        parameters_dict[line.strip().split(':')[0]] = line.strip().split(':')[1]

access_token = ''
application_secret_key = ''


class VkPhotoInYaDisk:
    url = 'https://api.vk.com/method/'

    def __init__(self, ya_token, id_vk, id_ok):
        self.token_ya = ya_token
        self.id_vk = id_vk
        self.id_ok = id_ok
        self.params_vk = {
            'access_token': parameters_dict['token VK'],
            'v': '5.131'
        }
        self.headers_ya = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def _get_url_photo_vk(self, number_of_photos):
        photo_download_url = self.url + 'photos.get'
        photo_download_parameters = {
            'owner_id': self.id_vk,
            'album_id': 'wall',
            'extended': 1,
            'count': 50
        }
        req = requests.get(photo_download_url, params={**self.params_vk, **photo_download_parameters})
        items = req.json()['response']['items']
        dict_photos_vk = {}
        info_name = {}
        for like in items[:number_of_photos]:
            if like['likes']['count'] not in info_name.keys():
                info_name[like['likes']['count']] = 1
            else:
                info_name[like['likes']['count']] += 1
        for item in items[:number_of_photos]:
            name = item['likes']['count']
            date_add = datetime.fromtimestamp(item['date']).strftime('%d-%m-%y %H-%M-%S')
            if info_name[name] > 1:
                name = str(name) + ' ' + str(date_add)
            url_photo_max_size = item['sizes'][-1]['url']
            height = item['sizes'][-1]['height']
            width = item['sizes'][-1]['width']
            dict_photos_vk[name] = {
                'file_name': f'{str(name)}.jpg',
                'size': f'{str(height)}x{str(width)}',
                'url': url_photo_max_size
            }
            time.sleep(0.1)
        return dict_photos_vk

    def create_json(self, parameter_dict):
        write_json = []
        for val in parameter_dict.values():
            add_write_json = {
                'file_name': val['file_name'],
                'size': val['size'],
            }
            write_json.append(add_write_json)
        with open('foto_info.json', 'w') as file_json:
            json.dump(write_json, file_json, indent=4)

    def upload_to_yandex(self, dict_load):
        self.name_dir = str(date.today())
        create_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.params_create_dir = {
            'path': str(self.name_dir)
        }
        requests.put(create_dir_url, headers=self.headers_ya, params=self.params_create_dir)
        url_upload_to_ya = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        for key, val in tqdm(dict_load.items()):
            params_upload_to_ya = {
                'path': f'{self.name_dir}/{str(key)}',
                'url': val['url']
            }
            requests.post(url_upload_to_ya, headers=self.headers_ya, params=params_upload_to_ya)

    def public_access(self):
        url_published_resources = 'https://cloud-api.yandex.net/v1/disk/resources/public'
        published_resources = requests.get(url_published_resources, headers=self.headers_ya)
        items = published_resources.json()
        for item in items['items']:
            if item['name'] == str(self.name_dir):
                return print(item['public_url'])
                break
            else:
                url_publishing = 'https://cloud-api.yandex.net/v1/disk/resources/publish'
                requests.put(url_publishing, headers=self.headers_ya, params=self.params_create_dir)
                self.public_access()

    def _get_url_photos_ok(self, access_token, application_secret_key, number_of_photos):
        session_secret_key = md5(
            '{}{}'.format(access_token, application_secret_key).encode('utf-8')).hexdigest().lower()
        url_ok = 'https://api.ok.ru/fb.do'
        params_ok = {
            'format': 'json',
            'method': 'photos.getPhotos',
            'application_key': 'CBAMLJKGDIHBABABA',
            'fid': self.id_ok,
            'count': number_of_photos,
            'fields': 'photo.like_summary, photo.pic_max, photo.created_ms, photo.standard_height, photo.standard_width'
        }
        param_sig = ''.join(['{}={}'.format(key, params_ok[key]) for key in sorted(params_ok.keys())])
        params_add_sig = {'sig': md5(f'{param_sig}{session_secret_key}'.encode('utf-8')).hexdigest().lower()}
        params_add_sig['access_token'] = access_token
        req = requests.get(url_ok, params={**params_ok, **params_add_sig})
        items = req.json()['photos']
        dict_photos_ok ={}
        info_name = {}
        for like in items:
            if like['like_summary']['count'] not in info_name.keys():
                info_name[like['like_summary']['count']] = 1
            else:
                info_name[like['like_summary']['count']] += 1
        for item in items:
            name = item['like_summary']['count']
            date_add = datetime.fromtimestamp(int(item['created_ms']/1000)).strftime('%d-%m-%y %H-%M-%S')
            if info_name[name] > 1:
                name = str(name) + ' ' + str(date_add)
            url_photo_max_size = item['pic_max']
            height = item['standard_height']
            width = item['standard_width']
            dict_photos_ok[name] = {
                'file_name': f'{str(name)}.jpg',
                'size': f'{str(height)}x{str(width)}',
                'url': url_photo_max_size
            }
            time.sleep(0.1)
        return dict_photos_ok

    def save_photos(self, number_of_photos=5):
        dict_ok = self._get_url_photos_ok(access_token, application_secret_key, number_of_photos)
        dict_vk = self._get_url_photo_vk(number_of_photos)
        self.upload_to_yandex({**dict_ok, **dict_vk})
        self.public_access()
        self.create_json({**dict_ok, **dict_vk})

Durov = VkPhotoInYaDisk(parameters_dict['token Ya'], id_vk=54, id_ok=535313956269)
Durov.save_photos()