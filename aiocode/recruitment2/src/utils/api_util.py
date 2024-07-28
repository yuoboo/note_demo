from sanic.response import HTTPResponse


def format_request_args(value):
    params = {}
    for key in value.keys():
        params[key] = value.get(key, None)
    return params


def cors(request):
    allow_headers = [
        'Authorization',
        'content-type'
    ]
    headers = {
        'Access-Control-Allow-Methods':
            ', '.join(request.app.router.get_supported_methods(request.path)),
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Headers': ', '.join(allow_headers),
    }
    return HTTPResponse('', headers=headers)
