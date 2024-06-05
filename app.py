import json
from datetime import datetime
import pytz
from wsgiref.simple_server import make_server


def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ.get('REQUEST_METHOD')

    if method == 'GET':
        tz_name = path if path else 'GMT'
        try:
            tz = pytz.timezone(tz_name)
            current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            response_body = f"<html><body>Current time in {tz_name}: {current_time}</body></html>"
            status = '200 OK'
        except pytz.UnknownTimeZoneError:
            response_body = f"<html><body>Unknown timezone: {tz_name}</body></html>"
            status = '400 Bad Request'

        response_headers = [('Content-Type', 'text/html')]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]

    elif method == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)

        if path == 'api/v1/convert':
            date_str = data['date']['date']
            source_tz = data['date']['tz']
            target_tz = data['target_tz']

            try:
                source_tz_obj = pytz.timezone(source_tz)
                target_tz_obj = pytz.timezone(target_tz)
                source_time = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
                source_time = source_tz_obj.localize(source_time)
                target_time = source_time.astimezone(target_tz_obj)
                response_body = json.dumps({'converted_time': target_time.strftime('%Y-%m-%d %H:%M:%S')})
                status = '200 OK'
            except (pytz.UnknownTimeZoneError, ValueError) as e:
                response_body = json.dumps({'error': str(e)})
                status = '400 Bad Request'

        elif path == 'api/v1/datediff':
            first_date_str = data['first_date']
            first_tz = data['first_tz']
            second_date_str = data['second_date']
            second_tz = data['second_tz']

            try:
                first_tz_obj = pytz.timezone(first_tz)
                second_tz_obj = pytz.timezone(second_tz)
                first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
                first_date = first_tz_obj.localize(first_date)
                second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
                second_date = second_tz_obj.localize(second_date)
                diff_seconds = int((second_date - first_date).total_seconds())
                response_body = json.dumps({'difference_in_seconds': diff_seconds})
                status = '200 OK'
            except (pytz.UnknownTimeZoneError, ValueError) as e:
                response_body = json.dumps({'error': str(e)})
                status = '400 Bad Request'

        else:
            response_body = json.dumps({'error': 'Unknown endpoint'})
            status = '404 Not Found'

        response_headers = [('Content-Type', 'application/json')]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]

    else:
        response_body = json.dumps({'error': 'Method not allowed'})
        status = '405 Method Not Allowed'
        response_headers = [('Content-Type', 'application/json')]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]


if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()