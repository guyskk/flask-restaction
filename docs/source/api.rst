.. _api:

API
===

.. module:: flask_restaction

这里涵盖了flask_restaction 提供 的所有接口。


Api
------------------

.. autoclass:: Api
   :members:
   :undoc-members:
   :inherited-members:

Resource
------------------

.. autoclass:: Resource
   :members:
   :undoc-members:


Permission
------------------

.. autoclass:: Permission
   :members:
   :inherited-members:

res.js
------------------

.. code-block:: javascript

   /*以下为jinja2模板，用于生成js*/
    
    {% for name,auth_header,actions in reslist %}
    res.{{name}}={};
        {% for url, meth, action, needtoken in actions %}
        res.{{name}}.{{action}}=function(data,fn,progress){
            header={};
            {% if needtoken %}
            addToken(header,"{{auth_header}}");
            {% endif %}
            var _fn=function(err, data, header, xhr){
                saveToken(header,"{{auth_header}}");
                if(typeof(fn)==="function"){
                    fn(err, data, header, xhr);
                }
            }
            res.ajax("{{url}}",{
                method:"{{meth}}",
                data:data,
                header: header,
                fn:_fn,
                progress:progress
            });
        };
        {% endfor %}
    {% endfor %}
    
    /*End jinja2模板*/



Validater
------------------

.. module:: validater

.. automodule:: validater.validate
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. automodule:: validater.validaters
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: validater.ProxyDict
   :members:
   :undoc-members:
