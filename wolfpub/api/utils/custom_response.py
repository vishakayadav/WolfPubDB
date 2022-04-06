from flask import Response
import json


class CustomResponse(Response):
    def __init__(self, data: dict = None, error: str = None, status_code: int = 200, message: str = 'OK', **kwargs):
        response_object = {
            'message': message,
            'status_code': status_code
        }
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'application/json'
        try:
            try:
                response_object['status_code'] = int(status_code)
            except ValueError:
                response_object['status_code'] = 500
                raise ValueError('invalid literal for int() with base 10')

            if not isinstance(message, str):
                raise ValueError('Message not in string format. Please use the right format')

            if error is None and (isinstance(data, str) or isinstance(data, bytes)):
                raise ValueError('Data can be str only when error in response')
            if error:
                if not isinstance(error, str):
                    raise ValueError('Error not in string format. Please use the right format')
                response_object['error'] = error
            else:
                if isinstance(data, list):
                    response_object['data'] = data
                elif isinstance(data, dict):
                    response_object['data'] = data
                    if 'data' in data:
                        response_object['data'] = data['data']
                    if 'message' in data:
                        response_object['message'] = data['message']
                else:
                    raise ValueError('Unsupported Data Structure: We only dictionary and list')
        except ValueError as e:
            response_object['status_code'] = 500
            response_object['message'] = e.__str__()
            response_object['error'] = 'CustomResponse'
        finally:
            print(response_object)
            return super(CustomResponse, self).__init__(response=json.dumps(response_object),
                                                        status=response_object['status_code'],
                                                        **kwargs)