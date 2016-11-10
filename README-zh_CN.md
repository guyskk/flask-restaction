# Flask-Restaction

[![travis-ci](https://api.travis-ci.org/guyskk/flask-restaction.svg)](https://travis-ci.org/guyskk/flask-restaction) [![codecov](https://codecov.io/gh/guyskk/flask-restaction/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/flask-restaction)

[README](README.md) | [中文文档](README-zh_CN.md)

为RESTful API而生的Web框架：

- 创建RESTful API
- 校验用户输入以及将输出转化成合适的响应格式
- 身份验证和权限控制
- 自动生成Javascript SDK和API文档

注意：仅支持Python3.3+


## 安装

    pip install flask-restaction


## 文档

简体中文文档: http://restaction-zh-cn.readthedocs.io/  
English Document: http://restaction.readthedocs.io/    
文档源文件: https://github.com/restaction    


## 测试

测试之前: 

    pip install -r requires.txt
    pip install -r requires-dev.txt
    pip install -e .
    python server/index.py

单元测试: 

    pytest

代码风格测试:
    
    flake8
    
集成测试: 

    tox


## License

MIT License
