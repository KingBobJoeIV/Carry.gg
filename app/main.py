from flask import Flask
from floodgate.flask import guard

from app.db import db
from app.internal.constants import DATABASE_URL, IS_PROD
from app.internal.helpers import ip_resolver
from app.internal.helpers.client_errors import method_not_allowed, not_found
from app.middlewares import Middleware, cors, process_time
from app.routes import common, user

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.url_map.strict_slashes = False


@app.before_request
@guard(ban_time=5, ip_resolver=ip_resolver, request_count=50, per=15)
def gate_check():
    pass


app.register_blueprint(common.router)
app.register_blueprint(user.router)

app.register_error_handler(404, not_found)
app.register_error_handler(405, method_not_allowed)

m = Middleware(app)
m.add_middleware(process_time.middleware)
m.add_middleware(cors.middleware)
