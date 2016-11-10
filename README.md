# Flask-Restaction

[![travis-ci](https://api.travis-ci.org/guyskk/flask-restaction.svg)](https://travis-ci.org/guyskk/flask-restaction) [![codecov](https://codecov.io/gh/guyskk/flask-restaction/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/flask-restaction)

[README](README.md) | [中文文档](README-zh_CN.md)

A web framwork born to create RESTful API

- Create RESTful API
- Validate request and Serialize response
- Authorization and Permission control
- Auto generate Javascript SDK and API document

Note: Only support Python3.3+


## Install

    pip install flask-restaction


## Document

简体中文文档: http://restaction-zh-cn.readthedocs.io/  
English Document: http://restaction.readthedocs.io/    
Document Sources: https://github.com/restaction   


## Test

Before test: 

    pip install -r requires.txt
    pip install -r requires-dev.txt
    pip install -e .
    python server/index.py

Pytest: 

    pytest

Code style:
    
    flake8
    
Tox test: 

    tox


## License

MIT License
