from app.models.user import UserSession
from flask import request, g
from typing import Callable, TypeVar, Generic

M = TypeVar("M")


class Context(Generic[M]):
    body: M

    def __init__(self, model: Callable[[], M] = None):
        self._reqest = request
        self.json = request.get_json() or {}
        self.body = model(**self.json) if model else None
        self.headers = request.headers
        self.auth: UserSession = g._auth_state  # pylint: disable=E0237
