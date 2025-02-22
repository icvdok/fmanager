from flask import Flask

def create_app():
    app = Flask(__name__)
    with app.app_context():
        from . import home, fcategory, fsearch, fcreate
        app.register_blueprint(home.bp)
        app.register_blueprint(fcategory.bp)
        app.register_blueprint(fsearch.bp)
        app.register_blueprint(fcreate.bp)
        return app