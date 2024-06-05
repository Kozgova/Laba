import unittest
import json
from app import application
from io import BytesIO

class TestApp(unittest.TestCase):
    def make_request(self, path, method='GET', body=None):
        environ = {
            'PATH_INFO': path,
            'REQUEST_METHOD': method,
            'wsgi.input': BytesIO(body.encode('utf-8')) if body else BytesIO(b''),
            'CONTENT_LENGTH': len(body) if body else 0,
        }
        headers_set = []
        body = []

        def start_response(status, headers):
            headers_set[:] = [status, headers]

        result = application(environ, start_response)
        body.extend(result)
        return headers_set[0], b''.join(body).decode('utf-8')

    def test_get_gmt_time(self):
        status, response = self.make_request('/')
        self.assertIn('200 OK', status)
        self.assertIn('Current time in GMT', response)

    def test_convert_time(self):
        data = json.dumps({
            'date': {'date': '12.20.2021 22:21:05', 'tz': 'EST'},
            'target_tz': 'Europe/Moscow'
        })
        status, response = self.make_request('/api/v1/convert', method='POST', body=data)
        self.assertIn('200 OK', status)
        self.assertIn('converted_time', response)

    def test_datediff(self):
        data = json.dumps({
            'first_date': '12.06.2024 22:21:05',
            'first_tz': 'EST',
            'second_date': '12:30pm 2024-02-01',
            'second_tz': 'Europe/Moscow'
        })
        status, response = self.make_request('/api/v1/datediff', method='POST', body=data)
        self.assertIn('200 OK', status)
        self.assertIn('difference_in_seconds', response)

if __name__ == '__main__':
    unittest.main()