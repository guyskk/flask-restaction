.. _schema:

YAML与Schema语法
================

JSON的语法是YAML语法的子集，因此大部分的JSON文件都可以被YAML的解析器解析。
由于YAML的运作主要依赖缩进来决定结构，且字符串不需要双引号，写出的Schema会更加精简，更适合写在文档字符串中。

`Validater <https://github.com/guyskk/validater>`_ 中使用JSON格式表示Schema，
框架中则用的是YAML，是为了适合不同的使用环境。

学习Schema语法需要先学会基本的JSON和YAML语法，YAML语法比JSON语法略复杂一些，可以通过 `YAML 语言教程
<http://www.ruanyifeng.com/blog/2016/07/yaml.html>`_ 对YAML语法进行初步了解。

之后可以看一下 `Validater <https://github.com/guyskk/validater>`_ 的文档，
Schema语法是基于JSON的，并且与实际数据结构相同，很容易学会。

然后再转换到YAML格式的Schema，新手学习过程中可能会遇到一些问题，
这里总结了一些与Schema相关的语法，方便上手。


字符串
-----------

YAML中有一些特殊符号，``@`` 是YAML的保留符号，``&`` 用于表示锚，这两个与Schema语法有冲突，
所以 ``@`` , ``&`` 开头的字符串都需要加上引号。

例如::
        
        "@user"

        userid: "@userid"

        friends:
            - "@user"

        "&optional&unique"


列表
-----------

注意: ``-`` 后面要有一个空格或换行。

简单的列表::

    # tags
    - "&unique&minlen=1"
    - str

嵌套的列表::

    # time_table
    # 星期一
    - - 上午写BUG
      - 下午改BUG
      - 晚上又写BUG
    # 星期二
    - - 上午改昨天的BUG
      - 下午又写一堆BUG
      - 晚上改不完的BUG
    # ...

    # schema_of_time_table
    - "&minlen=7&maxlen=7" # 一周七天
    - - "&minlen=3&maxlen=3" # 每天有三个时间段
      - str&optional # 这个时间段的安排


字典
-----------

注意: ``:`` 后面要有一个空格或换行。

简单的字典::

    user:
        id?int: user id
        name?str: user name

嵌套的字典::

    friends:
        best:
            $self: best friend
            id?int: user id
            name?str: user name
        bad:
            $self: bad friend
            id?int: user id
            name?str: user name

    friends:
        best@user: best friend
        bad@user: bad friend


复杂的嵌套
----------

列表里面是字典::

    - my friends
    - id?int: user id
      name?str: user name

    - my friends
    - "@user"

字典里面有列表::

    friends:
        - my friends
        - id?int: user id
          name?str: user name

    friends:
        - my friends
        - "@user"


Shared Schema
---------------

普通的Shared::

    $shared:
        userid: int
        tags:
            - "&unique&minlen=1"
            - str
        user:
            id?int: user id
            name?str: user name

下面的可以引用上面的::

    $shared:
        userid: int
        user:
            id@userid: user id
            name?str: user name
        
继承和拓展::

    $shared:
        paging:
            page_num?int&min=1&default=1: 第几页
            page_size?int&min=1&default=10: 每页的数量
        query:
            $self@paging: 查询参数
            tag?str: 标签
            date?date: 日期



