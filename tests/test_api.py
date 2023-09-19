import re
import unittest
from os import environ

from cloud_managment.cloud_api import YandexApi


class Test(unittest.TestCase):
    def test_environ_vars(self):
        YC_TOKEN = environ.get('YC_TOKEN')
        YC_CLOUD_ID = environ.get('YC_CLOUD_ID')
        YC_FOLDER_ID = environ.get('YC_FOLDER_ID')
        self.assertIsNotNone(YC_TOKEN)
        self.assertIsNotNone(YC_CLOUD_ID)
        self.assertIsNotNone(YC_FOLDER_ID)


class TestApi(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.api = YandexApi()

    def test_assert_is_instance(self):
        self.assertIsInstance(self.api, YandexApi)

    def test_get_resources(self):
        self.images = self.api.get_images()
        self.assertGreater(len(self.images), 0)
        self.assertIsInstance(self.images, list)
        # __import__('pprint').pprint(self.images)

    def test_check_pagesize(self):
        pagesize = '0'
        responce = self.api.get_images(pagesize=pagesize)
        print(f'{len(responce)=}')
        self.assertIsNotNone(responce)

    # @unittest.skip('Not time!')
    def test_check_resources(self):
        # {'createdAt': '2021-11-24T17:08:30Z',
        #  'description': 'debian 10',
        #  'family': 'debian-10',
        #  'folderId': 'standard-images',
        #  'id': 'fd804nmi5gak42ae1dcq',
        #  'minDiskSize': '3221225472',
        #  'name': 'debian-10-v20211124',
        #  'os': {'type': 'LINUX'},
        #  'pooled': True,
        #  'productIds': ['f2eplucasqut7r1kfafp'],
        #  'status': 'READY',
        #  'storageSize': '1665138688'}
        image_fields = ('createdAt', 'description', 'family',
                        'folderId', 'id', 'minDiskSize', 'name',
                        'os', 'pooled', 'productIds', 'status', 'storageSize'
                        )

        self.images = self.api.get_images()
        for image in self.images:
            self.assertIsInstance(image, dict)

            for parametr in image_fields:
                value = image.get(parametr)

                if parametr == 'os':
                    self.assertIsInstance(value, dict)
                elif parametr == 'productIds':
                    self.assertIsInstance(value, list)

    # @unittest.expectedFailure
    def test_find_image(self):
        image = 'ubuntu-20'
        pattern = 'ubuntu\s*-+\s*20'
        # self.assertIsNotNone(re.search(pattern, image))

        responce = self.api.get_images()
        for image in responce:
            isoname = image.get('name')
            print(f'{isoname=}')
            if re.search(pattern, isoname):
                break

        ubuntu_image = image.get('name')
        self.assertRegex(ubuntu_image, pattern)
        print(f'{ubuntu_image=}')

    def test_instances(self):
        instances = self.api.get_instances()
        self.assertIsNotNone(instances)
        self.assertGreater(len(instances), 1)
        self.assertIsInstance(instances, list)
        print(instances)


if __name__ == '__main__':
    unittest.main(failfast=True)
