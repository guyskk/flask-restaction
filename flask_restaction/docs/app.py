"""
# Hello World

简单介绍

**Mobi.css** 是一个*轻量、灵活*的移动端 CSS 框架。

只有 `3.6kb after gzip` ，比 Skeleton, Pure.css, Bootstrap v4 等所有 css 库都小
大量使用 Flexbox ，非常灵活， Homepage 基本上没有写额外的 css ，只有不到 10 行的 inline-style
Focus on mobile ，在 desktop 端相当于展示的还是 mobile 的页面，不过可以在左侧或右侧加上侧边栏

![V2EX](https://cdn.v2ex.co/site/logo@2x.png?m=1346064962)

![Photo](https://www.acyba.com/images/documentation/acymailing/tutorials/frontnewsmanagement/hidden.png)

> 只有 `3.6kb after gzip` ，比 Skeleton, Pure.css, Bootstrap v4 等所有 css 库都小
  大量使用 Flexbox ，非常灵活， Homepage 基本上没有写额外的 css ，只有不到 10 行的 inline-style
  Focus on mobile ，在 desktop 端相当于展示的还是 mobile 的页面，不过可以在左侧或右侧加上侧边栏

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
            .replace('$(meta)', json.dumps(api.meta, ensure_ascii=False))\
            .replace('$(res.js)', resjs)
    return make_response(content)

if __name__ == '__main__':
    app.run()
