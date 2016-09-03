from os.path import basename
from flask_restaction import Api
from flask import Flask, request, send_from_directory, make_response
app = Flask(__name__)
app.debug = True

api = Api(app, docs=__doc__)


class Hello:
    """欢迎"""

    def get(self, name):
        """
        Get hello

        $input:
            name?str: your name
        $output:
            welcome?str: welcome message
        """
        return {'welcome': name}

api.add_resource(Hello)

resjs = '?f=res.min.js'


@app.route('/docs')
def docs():
    mediatype = request.accept_mimetypes.best_match(
        ['text/html', 'application/json'], default='text/html')
    if mediatype == 'application/json':
        return api.meta_view()
    filename = request.args.get('f')
    if filename:
        return send_from_directory('./dist', basename(filename))
    with open('./docs.html') as f:
        content = f.read().replace('$(res.js)', resjs)
    return make_response(content)

if __name__ == '__main__':
    app.run()
