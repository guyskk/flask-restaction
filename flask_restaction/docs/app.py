"""
## PurePage

PurePage 致力于达到以下目标:

1. 良好的写作体验和阅读体验
2. 易于分享和发现有价值的文章
3. 运行稳定，安全，快速
4. 开放API

![PurePage](https://raw.githubusercontent.com/guyskk/purepage/master/artwork/logo.png)

> flask-restaction is awsome !!

$shared:
    paging:
        page_num?int&min=1&default=1: 第几页，从1开始计算
        page_size?int&min=1&default=10: 每页的数量
"""
import json
from os.path import basename
from flask_restaction import Api
from flask import Flask, request, send_from_directory, make_response
app = Flask(__name__)
app.debug = True

api = Api(app, docs=__doc__)
api.meta["$roles"] = {
    "管理员": {
        "hello": ["get", "post_login", "delete", "put", "post", "put_login"],
        "User": ["get", "post_login", "delete", "put", "post"],
        "Article": ["get", "post_login", "delete", "put"],
        "hello5": ["get", "post_login", "delete"],
        "hello6": ["get", "post_login"]
    },
    "普通用户": {
        "hello": ["get", "post_login"]
    },
    "访客": {
        "hello": ["post_login"]
    }
}


class Hello:
    """欢迎"""

    def get(self, name):
        """
        Get helloGet helloGet helloGet helloGet helloGet helloGet helloGet he

        $input:
            name?str: your name
        $output:
            welcome?str: welcome message
        """
        return {'welcome': name}

    def post(self, name):
        """
        Get hello

        $input:
            name?str: your name
        $output:
            welcome?str: welcome message
        """
        return {'welcome': name}

    def put(self, name):
        """
        Get hello

        $input:
            name?str: your name
        $output:
            welcome?str: welcome message
        """
        return {'welcome': name}


class User(Hello):
    """用户模块"""


class Article(Hello):
    """博客/文章"""


class World(Hello):
    """Hello World"""

api.add_resource(User)
api.add_resource(Hello)
api.add_resource(Article)
api.add_resource(World)
api.add_resource(type("Docs2", (), {"get": api.meta_view}))
resjs = '?f=res.min.js'


def get_title(desc):
    if not desc:
        return 'Docs'
    lines = desc.strip('\n').split('\n')
    if not lines:
        return 'Docs'
    return lines[0].strip('# ')


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
        content = f.read()\
            .replace('$(title)', get_title(api.meta.get('$desc')))\
            .replace('$(meta)', json.dumps(api.meta, ensure_ascii=False))\
            .replace('$(res.js)', resjs)
    return make_response(content)

if __name__ == '__main__':
    app.run()
