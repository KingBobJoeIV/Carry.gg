from os import environ, path
from pathlib import Path
from tempfile import gettempdir

IS_PROD = environ.get("IS_PROD") is not None

if not IS_PROD:
    print("assuming dev environment, add `IS_PROD` to your env to switch to dev")

# JWT Signing key, make sure this stays same or every user will need to relogin
SIGNING_KEY = environ.get("JWT_SIGNING_KEY")
# How long an access_token will last
TOKEN_EXPIRATION_TIME_IN_SECONDS = 60 * int(environ.get("TOKEN_EXPIRATION_TIME", 10))

FLASK_SECRET = environ.get("FLASK_SECRET")
DATABASE_URL = environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
REFRESH_TOKEN_SALT = environ.get("REFRESH_TOKEN_SALT")
DISABLE_CACHING = environ.get("DISABLE_CACHING") is not None
try:
    CACHE_DIR = Path(gettempdir(), "@cache").resolve()
    CACHE_DIR.mkdir(exist_ok=True)
except:
    CACHE_DIR = Path(path.dirname(path.realpath(__file__)), "@cache").resolve()
    CACHE_DIR.mkdir(exist_ok=True)
CACHE_DIR = str(CACHE_DIR)
print(f"[Cache] dir: {CACHE_DIR}")

STATIC_DIR = str(Path(path.dirname(path.realpath(__file__)), "..", "static").resolve())

del environ
del Path
del path
