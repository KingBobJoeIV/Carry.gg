from re import IGNORECASE
from re import compile as _compile

from app.exceptions import AppException

# pylint: disable=no-name-in-module
from psycopg2.errors import UniqueViolation

# regex to find the offending column
# there must be a better way - RH
find_error = _compile(
    r"Key\s*\(\"?(?P<key>.*?)\"?\)=\((?P<val>.*?)\)", IGNORECASE
).search


def get_integrity_error_cause(error_message: str):
    try:
        match = find_error(error_message)
        print(error_message)
        if not match:
            return None
        k = match.group("key")
        v = match.group("val")
        return k, v
    except Exception as e:
        print(e)
        return None


def check_integrity_error(e):
    # pylint: disable=E1101
    orig = getattr(e, "orig", None)
    if isinstance(orig, UniqueViolation):
        args = orig.args[0]
        ret = get_integrity_error_cause(args)
        if ret is None:
            raise AppException("User exists", 400)
        k, v = ret
        raise AppException(f'Another account exists with the {k} "{v}"')
    raise e
    # pylint: enable=E1101
