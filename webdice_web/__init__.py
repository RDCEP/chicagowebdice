from flask import Flask
# from flask.ext.assets import Environment, Bundle
from flask import render_template

from flask_beaker import BeakerSession
# from flask_restful import Api, reqparse
from webdice_web.html_parser.web import DiceWebParser


session_opts = {
    'session.type': 'ext:memcached',
    'session.cookie_expires': True,
    'session.lock_dir': './data',
    'session.url': '127.0.0.1:11211',
    'session.memcache_module': 'pylibmc',
    'session.auto': True
}


app = Flask(__name__)
app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def not_found(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def not_found(error):
    return render_template('errors/500.html'), 500


@app.context_processor
def context_globals():
    return dict()


# api = Api(app)
# api_parser = reqparse.RequestParser()
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Ad78gii#$3979oklaklf'
BeakerSession(app)

from webdice_web.views import mod as work_module
app.register_blueprint(work_module)


if __name__ == '__main__':
    app.run()