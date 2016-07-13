function(root, init) {
    var q = init(root, '{{ auth_header }}', '{{ url_prefix }}');
    {% for resource in meta %}
    var r = root.{{ resource }} = {};
        {% for action, meta_action in meta[resource].items() -%}
        r.{{ action }} = q('{{ meta_action["$url"] }}', '{{ meta_action["$httpmethod"] }}');
        {% endfor %}
    {%- endfor %}
}
