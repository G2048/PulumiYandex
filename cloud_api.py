import re
import os
import json
import requests
import logging.config
import unittest

from abc import ABC, abstractmethod
from requests import exceptions
from settings import LogConfig, YC_TOKEN

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')
logger.setLevel(20)


class IApi(ABC):

    @abstractmethod
    def get_images(self):
        pass


class YandexApiFactory:
    '''curl.exe -H "Authorization: Bearer $Env:YC_TOKEN"
    "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    '''

    __instance = None
    API_URL = 'https://compute.api.cloud.yandex.net/'
    # IAM_TOKEN = os.environ.get('YC_TOKEN')
    IAM_TOKEN = YC_TOKEN
    HEADERS = {'Authorization': f'Bearer {IAM_TOKEN}'}

    def __new__(cls, ):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self,):
        pass

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except exceptions.JSONDecodeError as e:
            return False

    def _request(self, url, params, *args, **kwargs):
        logger.debug(f'{url}, {params=}, {self.HEADERS=}')
        responce = requests.get(url=url, params=params, headers=self.HEADERS)
        logger.debug(responce.status_code)

        if responce.ok:
            data_json = self._validateJson(responce.json)

            if data_json:
                return data_json
            else:
                return responce.text


class YandexApi(IApi, YandexApiFactory):
    def __init__(self, ):
        super().__init__()

    # "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    def get_images(self, *, imagestype='standard-images', pagesize='100') -> list:
        PARAMS = {'folderId': imagestype, 'pageSize': pagesize}
        ready_url = f'{self.API_URL}compute/v1/images'
        images = self._request(url=ready_url, params=PARAMS).get('images')
        return images


class Image:

    def __init__(self, IApi):
        self.api = IApi

    def find_image(self, pattern='ubuntu-20'):
        images = self.api.get_images()

        for image in images:
            isoname = image.get('name')
            if isinstance(isoname, str) and isoname.startswith(pattern):
                self._image = image
                break

        return self

    def filds(self,):
        self.id = self._image.get('id')
        self.name = self._image.get('name')
        self.created = self._image.get('createdAt')
        self.family = self._image.get('family')
        self.mindisksize = self._image.get('minDiskSize')
        self.pooled = self._image.get('pooled')
        self.status = self._image.get('status')
        self.storagesize = self._image.get('storageSize')

        return self


if __name__ == '__main__':
    api = YandexApi()
    api.get_images()
    # resources = ResourcesAPI(api=YandexAPI)
    # resources.api.get_images()
