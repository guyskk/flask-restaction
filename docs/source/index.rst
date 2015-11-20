:orphan:

Welcome to Flask-Restaction!
============================================

欢迎阅读 Flask-Restaction 的文档。

在这之前你需要对 Flask 有一定的了解，我推荐您阅读
`《Flask 中文文档》 <http://dormousehole.readthedocs.org/en/latest/index.html>`_ 。

Flask-Restaction 依赖 validater 校验输入输出，欲知详情请移步 
`《validater 文档》 <https://github.com/guyskk/validater>`_ 。

阅读完《 :ref:`quickstart` 》之后，建议您阅读《 :ref:`api` 》，这样能对 Flask-Restaction 有更深入的了解。另外， example 目录中有几个示例，其中包含了框架的绝大部分用法。


Flask-Restaction 是什么
--------------------------

Flask-Restaction 是一个为 RESTful API 而生的 Web 框架

- 创建 RESTful API
    
- 校验用户输入以及将输出转化成合适的响应格式
    
- 身份验证和权限控制

- 易于测试

- 自动生成 res.js 和 API 文档
    
- 支持 python3


安装
-------

.. code:: python

    pip install flask-restaction



用户指南
--------------
.. toctree::
   :maxdepth: 2

   quickstart
   resjs


API参考
--------------
.. toctree::
   :maxdepth: 2   

   api
   validater
