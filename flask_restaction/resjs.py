#!/usr/bin/env python
import argparse
from flask_restaction.gen import resjs


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="url of api")
    parser.add_argument("-d", "--dest", default=".",
                        help="dest dir to save res.js and res.min.js")
    args = parser.parse_args()
    print(args)
    resjs(args.url, args.dest)

if __name__ == '__main__':
    cli()
