from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from config import config
from datetime import datetime,date
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet,IMAGES,configure_uploads,ALL,patch_request_class


db = SQLAlchemy()
csrf = CSRFProtect()
photos = UploadSet('PHOTO')

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    csrf.init_app(app)
    configure_uploads(app, photos)
    patch_request_class(app,size=None)

    def format_datetime(value):
        return date.fromtimestamp(value)


    app.jinja_env.filters['datetime'] = format_datetime

    # 注册公用蓝图
    from .common import common as common_blueprint
    app.register_blueprint(common_blueprint)

    # 注册首页蓝图
    from .index import home as home_blueprint
    app.register_blueprint(home_blueprint)

    #注册后台蓝图
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint,url_prefix = "/melon")

    return app

@csrf.error_handler
def csrf_error(reason):
    return render_template('common/404.html', reason=reason), 400