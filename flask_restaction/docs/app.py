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
$error:
    404.NotFound: 未找到页面
    500.ServerError: 服务器错误
"""
from flask_restaction import Api
from flask import Flask
app = Flask(__name__)
app.debug = True
app.config['API_URL_PREFIX'] = '/api'

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
api.add_resource(type("Docs", (), {"get": api.meta_view}))


app.route('/')(api.meta_view)
if __name__ == '__main__':
    app.run()
