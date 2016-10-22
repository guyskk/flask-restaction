"""
Flask-Restaction

http://flask-restaction.readthedocs.org
"""
from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'requires.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name="flask-restaction",
    version="0.25.2",
    description="A web framwork born to create RESTful API",
    long_description=__doc__,
    author="guyskk",
    author_email='guyskk@qq.com',
    url="https://github.com/guyskk/flask-restaction",
    license="MIT",
    packages=["flask_restaction"],
    entry_points={
        'console_scripts': ['resjs=flask_restaction.cli:main'],
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
