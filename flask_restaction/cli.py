import os
import argparse
import requests
from jinja2 import Template
from .res import res_to_url


def parse_meta(url):
    meta = requests.get(url).json()
    meta2 = {}
    for resource_name in meta:
        if resource_name.startswith("$"):
            continue
        meta2[resource_name] = resource = {}
        for action in meta[resource_name]:
            if action.startswith("$"):
                continue
            url, httpmethod = res_to_url(resource_name, action)
            resource[action] = {
                "$url": url,
                "$httpmethod": httpmethod
            }
    return meta["$url_prefix"], meta["$auth"]["header"], meta2


def read_file(fpath):
    fpath = os.path.join(os.path.dirname(__file__), fpath)
    with open(fpath, encoding="utf-8") as f:
        return f.read()


def save_file(dest, content):
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)


def resjs(url, dest):
    """Generate res.js

    :param url: url of api
    :param dest: dest dir path
    """
    url_prefix, auth_header, meta = parse_meta(url)
    tmpl = read_file('tmpl/res-core.js')
    rendered = Template(tmpl).render(
        url_prefix=url_prefix,
        auth_header=auth_header,
        meta=meta
    )

    resjs = read_file('resjs/dist/res.js')
    resjs = resjs.replace('"#res-core.js#"', rendered)
    save_file(os.path.join(dest, "res.js"), resjs)

    resminjs = read_file('resjs/dist/res.min.js')
    resminjs = resminjs.replace('"#res-core.js#"', rendered)
    name, ext = os.path.splitext(dest)
    save_file(os.path.join(dest, 'res.min.js'), resminjs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="url of api")
    parser.add_argument("-d", "--dest", default=".",
                        help="dest dir to save res.js and res.min.js")
    args = parser.parse_args()
    resjs(args.url, args.dest)
