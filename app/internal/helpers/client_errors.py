from app.internal.helpers import json_response, get_origin
from flask import request, render_template


def not_found(e):
    return render_template("404.html"), 404


def rate_limit_exceeded(e):
    return render_template("429-500.html"), 429, 500


def method_not_allowed(e):
    return json_response(
        {"error": "Method not allowed"},
        status=405,
        headers={"access-control-allow-origin": get_origin(request)},
    )