import datetime

from flask import Flask
from flask_nameko import FlaskPooledClusterRpcProxy
import config

from app.admin import admin
from app.user import user
from flask_cors import CORS
from flasgger import Swagger,swag_from
rpc = FlaskPooledClusterRpcProxy()

def create_app():
    app = Flask(__name__)
    CORS(app, resources=r"/*")  # 允许所有域名跨域
    app.config.from_object('config')
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
    swagger = Swagger(app)
    rpc.init_app(app)

    return app

app = create_app()

from main import views
