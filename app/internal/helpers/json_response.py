from json import dumps
from flask import Response


def json_response(data: dict, status=200, headers=None) -> Response:
    dump = dumps(data)
    resp = Response(
        dump, status=status, headers=headers, content_type="application/json"
    )
    return resp