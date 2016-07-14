# REST-Action风格的Web架构

## 概要

REST-Action是基于REST的Web架构，目的是使REST架构标准化，提高易用性。

事实上，对RESTful的解释和理解多种多样，实现RESTful的方式或细节也有许多不同之处。
这些理解和实现整体上都是符合RESTful要求的，希望读者不要拘泥于理论或是个人理解，不要执着于争辩是不是RESTful。

REST-Action架构遵循实用原则，将状态转化（State Transfer）抽象为对资源的操作（Action）的概念，并将URL标准化，定义了元数据的格式，权限验证的内容。


## Resource和Action

**Resource**
    任何能够被命名的信息都能够作为一个资源。一个资源是到一组实体的概念上的映射， 是一组可能会随时间而变化的实体或值，而不是某个特定时刻与该映射相关联的实体本身。
   
**Action**
    对资源的操作，任何对该资源有意义的动词都能够作为一种操作，不局限于HTTP协议中规定的有限的几个方法。


## URL标准化

将Action限定为HTTP Method开头，例如 `get_sum`，下划线作为分隔符。这样可以很好的与HTTP协议兼容。

将Resource.Action转换为URL的过程也很直观： 将Action中HTTP Method取出，剩下部分作为URL。例如 `calculator.get_sum` 转换为 `GET /calculator/sum`。

## 请求与响应

用HTTP状态码表示请求状态，通常：请求成功200,业务逻辑问题400,权限问题403,服务器错误500。

在请求头/响应头中传递状态信息，例如：Authorization，ETag，Accept，Content-Type。


## Meta元数据

Resource是最小的功能集合，多个Resource组合成API。
规定Resource路径的共同部分为url_prefix，通过`GET url_prefix` 获取元数据。

元数据中包含了API自身的信息和每个Resource的信息，Resource的信息包含了其中每个Action的输入/输出格式以及请求失败可能返回的错误信息。

输入输出格式用 [同构的JSON-Schema](https://github.com/guyskk/validater/blob/master/Isomorph-JSON-Schema.md) 描述。

错误信息包含2部分，一部分是给程序使用的（用于判断具体的错误），一部分是给用户看的（提示用户）。

    {
        “error": "ErrorCode", 
        "message": "提示用户的信息"
    } 

错误码命名用大驼峰形式的字符串，例如：InvalidData,Timeout,UserAlreadyExisted。


## 资源发现和资源依赖

参考众多的包管理器，npm, pip, yum, apt-get等等，它们都很好的解决了资源依赖问题。

因此，需要一个统一的资源管理中心，注册资源只需要提供一个唯一名称和一个url_prefix，
由资源管理中心自动获取API的元数据，解析其中的依赖和版本，注册成功之后便能供他人使用。

API版本信息放在请求头(Accept)中。例如：`Accept: application/json;version=3`

## 身份验证

操作需要授权的Resource，请求方需在请求头Authorization设置Token。
Token中是JWT签名后的用户身份信息，服务方依据此Token判断用户身份并验证权限。

Token是明文的，客户端可以查看但不能修改，故其中不能含有安全敏感信息。


## 元数据格式

所有以`$`开头的键用于描述API本身的信息。这样可以减少元数据层级，便于阅读。

    {
        "$desc": "简介",
        "$url_prefix": "Resource路径的共同前缀，最后不带'/'",
        "$requires":{
            "name": "version",
            ...
        }
        "$auth": {
            "algorithm": "HS256",
            "expiration": 3600,
            "header": "Authorization"
        },
        "$roles": {
            "Role": {
                "Resource": ["Action", ...],
                ...
            },
            ...
        },
        "$shared": {
            "name": "Schema",
            ...
        },
        "$error": {
            "ErrorCode": "通用错误码的含义",
            ...
        },
        "Resource":{
            "$shared": {
                "name": "Schema",
                ...
            },
            "Action":{
                "$desc":"简介",
                "$input":"输入Schema",
                "$output":"输出Schema",
                "$error":{
                    "ErrorCode": "错误码的含义",
                    ...
                }
            },
            ...
        },
        ...
    }


## 实现

REST-Action架构不限于特定语言和特定框架。
