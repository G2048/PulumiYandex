import unittest
from cloud_api import YandexApi
from cloud_info import InfoInstance, InfoImage


class TestCloudInfo(unittest.TestCase):

    # def setUp(self):

    def test_get_ubuntu_image(self):
        image = InfoImage(YandexApi())
        ubuntu = image.find_image('ubuntu-20').filds()
        self.assertIsInstance(ubuntu._image, dict)
        # ubuntu.filds()

        self.assertIsNotNone(ubuntu.id)
        self.assertIsNotNone(ubuntu.name)
        self.assertIsNotNone(ubuntu.status)
        print(ubuntu.name)
        print(ubuntu.id)

    def test_instance_info(self):
        self.info = InfoInstance('fhm0htbn18lic96kgosh')
        self.assertIsNotNone(self.info.network)
        # self.assertIsNotNone(self.info.name)
        # print(self.info.name)


if __name__ == '__main__':
    unittest.main()
