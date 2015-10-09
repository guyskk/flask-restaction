"""http://flask-restaction.readthedocs.org/zh/latest/"""
from setuptools import setup
setup(
    name="flask-restaction",
    version="0.17.0",
    description="a powerful flask ext for create restful api",
    long_description=__doc__,
    author="kk",
    url="https://github.com/guyskk/flask-restaction",
    license="MIT",
    packages=["flask_restaction"],
    package_data={'flask_restaction': ['js/res.js', 'html/res_docs.html']},
    install_requires=[
        'flask>=0.1',
        'pyjwt>=1.4',
        'validater>=0.8.0',
        'six>=1.10.0',
    ],
    classifiers=[
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
