# Flask-Restaction

![travis-ci](https://api.travis-ci.org/guyskk/flask-restaction.svg) [![codecov](https://codecov.io/gh/guyskk/flask-restaction/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/flask-restaction)


为RESTful API而生的Web框架：

- 创建RESTful API
- 校验用户输入以及将输出转化成合适的响应格式
- 身份验证和权限控制
- 自动生成Javascript SDK和API文档

注意：仅支持Python3.3+

Flask-Restaction依赖[Validater](https://github.com/guyskk/validater)校验输入输出。


## 安装
    
    pip install flask-restaction


## 架构

[REST-Action风格的Web架构](REST-Action.md)

此项目是基于Flask框架实现的REST-Action风格的Web框架。
目前已具备雏形，但还没有实现所有特性。


## 文档

在线文档：http://flask-restaction.readthedocs.org/zh/latest/

手动构建文档：
    
    pip install sphinx
    cd docs
    make html


## 测试

测试之前需先运行一个服务器：

    cd server
    pip install -r requires.txt
    python index.py

用tox测试：

    pip install tox
    tox

用pytest测试：

    pip install pytest
    py.test tests


## 构建res.js

    // create a server for test
    cd server
    pip install -r requires.txt
    python index.py

    // build resjs
    cd flask_restaction/resjs
    npm install
    gulp
    
    // test
    npm install -g karma-cli
    karma start

## License 

MIT License
