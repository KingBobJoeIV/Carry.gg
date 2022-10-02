from flask import Request


def get_origin(request: Request):
    return request.headers.get("Origin", "*")
