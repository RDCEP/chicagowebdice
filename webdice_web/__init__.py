import glob
import os
from itertools import groupby
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask import render_template
from webdice_web.constants import BASE_DIR
# from flask_restful import Api, reqparse

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
# api = Api(app)
# api_parser = reqparse.RequestParser()
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Ad78gii#$3979oklaklf'


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def not_found(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def not_found(error):
    return render_template('errors/50x.html'), 500


@app.context_processor
def context_globals():
    return dict()

@app.context_processor
def glossary_terms():
    return dict(
        glossary_terms=[list(g) for k, g in groupby(map(
            lambda x: ''.join(x.split('/')[-1].split('.')[:-1]),
            glob.glob(os.path.join(
                BASE_DIR, 'templates', 'modules', 'glossary', 'terms',
                '*.html'))), key=lambda x: x[0])],
        advanced_glossary_terms=map(
            lambda x: ''.join(x.split('/')[-1].split('.')[:-1]),
            glob.glob(os.path.join(
                BASE_DIR, 'templates', 'modules', 'glossary', 'terms',
                'advanced', '*.html'))),
    )


from webdice_web.views import mod as work_module
app.register_blueprint(work_module)


assets = Environment(app)
js = Bundle('js/stacked_chart.js',
            'js/webdice_zoom.js',
            'js/webdice_param_eq.js',
            'js/webdice_download_svg.js',
            'js/webdice_download_csv.js',
            'js/main.js',
            'js/webdice_range_slider.js',
            'js/webdice_tabs.js',
            filters='jsmin', output='gen/webdice.js')
assets.register('js_webdice', js)
js = Bundle('js/vendor/d3.v3.min.js', 'js/vendor/json2.js',
            'js/vendor/modernizr.custom.27311.js',
            filters='jsmin', output='gen/vendor.js')
assets.register('js_vendor', js)
js = Bundle('js/vendor/fd-slider.min.js',
            filters='jsmin', output='gen/fd-slider.js')
assets.register('js_slider', js)
css = Bundle('css/main.css', 'css/fd-slider.min.css',
            filters='cssmin', output='gen/main.css')
assets.register('css_main', css)


if __name__ == '__main__':
    app.run()