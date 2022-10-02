# pylint: skip-file
from types import SimpleNamespace, GeneratorType
from typing import Callable, List
from flask import request, Response
from flask import Flask, g
from app.internal.helpers import guard


class State(SimpleNamespace):
    response: Response = None


def consume_next(g: GeneratorType):
    try:
        return next(g)
    except StopIteration:
        pass


class MiddlewareContext:
    _functions: List[Callable] = []
    _returns: List[GeneratorType] = None
    _state: State

    def __init__(self, functions: List[Callable]) -> None:
        self._functions = functions
        self._returns = []
        self._state = State()

    def before(self):
        state = self._state
        for i in self._functions:
            maybe_response: GeneratorType = i(request, state)
            if maybe_response is not None:
                if not isinstance(maybe_response, GeneratorType):
                    return maybe_response
                self._returns.append(maybe_response)
                consume_next(maybe_response)

    def after(self, response: Response):
        state = guard(self._state)
        state.response = response
        for i in guard(self._returns):
            maybe_response = consume_next(i)
            if maybe_response is not None:
                state.response = maybe_response
        response = state.response
        return response


class Middleware:
    _functions: List[Callable] = []
    def __init__(self, app: Flask):
        self.bind(app)

    def add_middleware(self, func):
        self._functions.append(func)

    def bind(self, app: Flask):
        app.before_request(self._before_request)
        app.after_request(self._after_request)

    def _before_request(self):
        ctx = MiddlewareContext(self._functions)
        g.__mdctx = ctx
        ctx.before()

    def _after_request(self, response: Response):
        return g.__mdctx.after(response)
