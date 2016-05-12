# Flask-Restaction

![travis-ci](https://api.travis-ci.org/guyskk/flask-restaction.svg)

Flask-Restaction is a web framwork born to create RESTful API

### You can do this Easily

- Create restful api 
- Validate inputs and Convert outputs
- Authorize and Permission control
- Auto generate res.js and document
- Support py3


### Install
    
    pip install flask-restaction


### Build Document

    cd docs
    make html

### Documents on Readthedocs

http://flask-restaction.readthedocs.org/zh/latest/

### Test

First, install test tools:

    pip install pytest
    pip install tox

Then, run tests

    py.test tests

    or

    tox

### res.js

    // create a server for test
    pip install -r server/requires.txt
    python server index.py

    // build resjs
    cd flask_restaction/resjs
    npm install
    gulp
    
    // test
    npm install -g karma-cli
    karma start

## license 

MIT License
