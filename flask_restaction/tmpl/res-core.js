function(root, init) {
    var q = init(root, '{{ apiinfo.auth_header }}', '{{ apiinfo.url_prefix }}');
    {% for res in apiinfo.resources %}
    var r = root.{{ res['name'] }} = {};
        {% for action in res['actions'] -%}
        r.{{ action.action}} = q('{{ action.url }}', '{{ action.method }}');
        {% endfor %}
    {%- endfor %}
}
