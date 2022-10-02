from flask import Request
from ._handler import State
from time import time


def middleware(request: Request, state: State):
    start = time()
    yield
    process = time() - start
    state.response.headers.add("x-process-time", str(round(process, 2)))
