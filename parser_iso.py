import os
import json
import requests
import logging.config

from abc import ABC, abstractmethod
from requests import exceptions
from settings import LogConfig

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')


class IApi(ABC):

    @abstractmethod
    def get_images(self):
        pass


class YandexApiFactory:
    '''curl.exe -H "Authorization: Bearer $Env:YC_TOKEN"
    "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    '''

    API_URL = 'https://compute.api.cloud.yandex.net/'

    def __init__(self,):
        self.READY_URL = None
        IAM_TOKEN = os.environ.get('YC_TOKEN')
        self.HEADERS = {'Authorization' : f'Bearer {IAM_TOKEN}' }

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except exceptions.JSONDecodeError as e:
            # logger.debug(e)
            return False

    def _request(self, *args, **kwargs):
        imagestype = 'standard-images'
        PARAMS = {'folderId': imagestype, 'pageSize': '100'}
        requests.get(self.READY_URL, params=PARAMS, headers=self.HEADERS)

class YandexAPI(IApi, YandexApiFactory):

    def __init__(self,):
        imagestype = 'standard-images'
        IAM_TOKEN = os.environ.get('YC_TOKEN')
        self.PARAMS = {'folderId': imagestype, 'pageSize': '100'}
        self.HEADERS = {'Authorization': f'Bearer {IAM_TOKEN}' }
        self.READY_URL = ''

    def get_images(self):
        print('Call get_images!')
        # self._request()



class ResourcesAPI():

    def __init__(self, api: IApi):
        self.api = api()


if __name__ == '__main__':
    resources = ResourcesAPI(api=YandexAPI)
    resources.api.get_images()
    # resources.get_images()
