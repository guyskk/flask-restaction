import os
import argparse
import requests
from .res import res_to_url

RESJS_DIST = os.path.join(os.path.dirname(__file__), 'resjs/dist')


def parse_meta(meta):
    """Parse metadata of API

    :param meta: metadata of API
    :return: url_prefix, auth_header, resources
    """
    resources = {}
    for name in meta:
        if name.startswith("$"):
            continue
        resources[name] = resource = {}
        for action in meta[name]:
            if action.startswith("$"):
                continue
            url, httpmethod = res_to_url(name, action)
            resource[action] = {
                "url": url,
                "method": httpmethod
            }
    url_prefix = meta.get("$url_prefix", "").rstrip("/")
    return url_prefix, meta["$auth"]["header"].lower(), resources


def read_file(filename):
    fpath = os.path.join(RESJS_DIST, filename)
    with open(fpath, encoding="utf-8") as f:
        return f.read()


def save_file(dest, content):
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)


def render_core(url_prefix, auth_header, resources):
    """Generate res.core.js"""
    code = ''
    code += "function(root, init) {\n"
    code += "  var q = init('%(auth_header)s', '%(url_prefix)s');\n" %\
        {'url_prefix': url_prefix, 'auth_header': auth_header}
    code += "  var r = null;\n"
    for key in resources:
        code += "  r = root.%(key)s = {};\n" % {'key': key}
        for action, item in resources[key].items():
            code += "    r.%(action)s = q('%(url)s', '%(method)s');\n" %\
                {'action': action,
                 'url': item['url'],
                 'method': item['method']}
    code += "}"
    return code


def generate_code(meta, prefix=None, node=False, min=False):
    """Generate res.js

    :param meta: tuple(url_prefix, auth_header, resources) or metadata of API
    :return: res.js source code
    """
    if isinstance(meta, dict):
        url_prefix, auth_header, resources = parse_meta(meta)
    else:
        url_prefix, auth_header, resources = meta
    if prefix is not None:
        url_prefix = prefix
    core = render_core(url_prefix, auth_header, resources)
    if min:
        filename = 'res.web.min.js'
    else:
        filename = 'res.web.js'
    if node:
        filename = 'res.node.js'
    base = read_file(filename)
    return base.replace('"#res.core.js#"', core)


def resjs(url, dest='./res.js', prefix=None, node=False, min=False):
    """Generate res.js and save it"""
    meta = requests.get(url, headers={'Accept': 'application/json'}).json()
    code = generate_code(meta, prefix, node, min)
    save_file(dest, code)


def main():
    parser = argparse.ArgumentParser(
        description="generate res.js for browser or nodejs")
    parser.add_argument("url", help="url of api meta")
    parser.add_argument("-d", "--dest", default="./res.js",
                        help="dest path to save res.js")
    parser.add_argument("-p", "--prefix", default="",
                        help="url prefix of generated res.js")
    parser.add_argument("-n", "--node", default=False, action='store_true',
                        help="generate res.js for nodejs, default for browser")
    parser.add_argument("-m", "--min", default=False, action='store_true',
                        help="minimize generated res.js, default not minimize")
    args = parser.parse_args()
    resjs(args.url, args.dest, args.prefix, args.node, args.min)
    print('OK, saved in: %s' % args.dest)
