from app.internal.helpers import json_response, get_origin
from flask import request


def not_found(e):
    return json_response(
        {"error": "not found"},
        status=404,
        headers={"access-control-allow-origin": get_origin(request)},
    )


def method_not_allowed(e):
    return json_response(
        {"error": "Method not allowed"},
        status=405,
        headers={"access-control-allow-origin": get_origin(request)},
    )