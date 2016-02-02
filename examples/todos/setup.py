# coding:utf-8
from setuptools import setup

setup(
    name="todos",
    version="1.0",
    description="a todos app",
    author="guyskk",
    author_email='1316792450@qq.com',
    install_requires=[
        "flask_restaction>=0.20.0",
        "sqlitedict>=1.4",
    ],
    packages=["todos"],
    tests_require=[
        'pytest',
    ],
)
