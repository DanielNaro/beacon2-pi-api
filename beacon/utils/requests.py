
from aiohttp.web_request import Request
from beacon.request.parameters import RequestParams
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level

@log_with_args(level)
async def check_request_content_type(self, request: Request):
    if request.headers.get('Content-Type') == 'application/json':
        post_data = await request.json()
    else:
        post_data = await request.post()
    return post_data

@log_with_args(level)
async def get_qparams(self, request: Request):
    json_body = await request.json() if request.method == "POST" and request.has_body and request.can_read_body else {}
    qparams = RequestParams(**json_body).from_request(request)
    return qparams