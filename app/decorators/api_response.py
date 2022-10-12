from enum import Enum, auto
from functools import wraps
from traceback import print_exc

from app.exceptions import AppException
from app.internal.helpers.json_response import json_response

# from app.models.user import UserSession
from flask import Response, g
from pydantic import ValidationError


class AuthModes(Enum):
    lax = auto()
    strict = auto()
    admin = auto()
    none = auto()


def decorate(handler, auth_mode=AuthModes.none):
    @wraps(handler)
    def run(*args, **kwargs):
        try:
            if auth_mode != AuthModes.none:
                g._auth_state = _auth(auth_mode)  # pylint: disable=E0237
            else:
                g._auth_state = None  # pylint: disable=E0237
            maybe_response = handler(*args, **kwargs)
            if isinstance(maybe_response, Response):
                return maybe_response
            return json_response({"data": maybe_response})
        except AppException as e:
            return e.to_flask_response()
        except ValidationError as e:
            return handle_validation_error(e)
        except Exception as e:
            print_exc()
            err = "An unknown error occured"
            return json_response({"error": err, "_tb": f"{e}"}, status=500)

    return run


def handle_validation_error(e):
    err = e.errors()
    message = []
    for i in err:
        loc = i["loc"]
        msg = i["msg"]
        message.append(f'"{loc[-1]}" - {msg}')
    return json_response({"error": ", ".join(message)}, status=422)




def _auth(auth_mode):
    strict = auth_mode == AuthModes.strict or auth_mode == AuthModes.admin
    sess = None
    if auth_mode == AuthModes.admin and not sess.is_admin:
        raise AppException("No.", 403)
    return sess


def _lax(handler):
    return decorate(handler, auth_mode=AuthModes.lax)


def _strict(handler):
    return decorate(handler, auth_mode=AuthModes.strict)


def _admin(handler):
    return decorate(handler, auth_mode=AuthModes.admin)


def api(handler):
    return decorate(handler, auth_mode=AuthModes.none)


api.none = api
api.lax = _lax
api.strict = _strict
api.admin = _admin
