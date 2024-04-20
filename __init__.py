import os

from flask import Flask
from . import db, auth, blog, calendar, editor, about
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=2, x_proto=2, x_host=2, x_prefix=2
    )
    app.config.from_mapping(
        SECRET_KEY='dev',       
        DATABASE=os.path.join(app.instance_path, 'notifier.sqlite'),
    )
    app.permanent_session_lifetime = timedelta(minutes=7)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=False)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(calendar.bp)
    app.register_blueprint(editor.bp)
    app.register_blueprint(about.bp)
    app.add_url_rule('/', endpoint='index')

    return app