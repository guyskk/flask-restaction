# coding:utf-8
from setuptools import setup

setup(
    name="todos",
    version="1.0",
    description="a todos app",
    author="guyskk",
    author_email='guyskk@qq.com',
    install_requires=[
        "flask>=0.10.1",
        "flask-restaction>=0.20.0",
        "flask-sqlalchemy>=2.1",
    ],
    packages=["todos"],
    include_package_data=True,
    tests_require=[
        'pytest',
    ],
)
