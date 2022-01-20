from unittest import mock, TestCase

from app import facebook, google, data


class TestApi(TestCase):
    
    @mock.patch.object(google, 'get_data', side_effect =  Exception('Error'))

    def test_external_api(self, google_mock):
        self.assertRaises(Exception, google_mock)

    

        
        