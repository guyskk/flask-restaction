# coding:utf-8



def gen_rules(app):
    rules = [{"host": r.host, "subdomain": r.subdomain, "rule": r.rule,
              "endpoint": r.endpoint, "methods": r.methods}
             for r in app.url_map.iter_rules() if r.rule[0:2] != '/_']
    sorted(rules, key=lambda x: x['endpoint'])
    return rules


def gen_res_list(app):
    rules = gen_rules(app)
    import re
    pattern = re.compile(ur'<((int|float|path):)?(.*)>', re.I)
    res_list = []
    for r in rules:
        ends = r['endpoint'].split('.')
        if len(ends) >= 2:
            name = ends[0]
            method_action = ends[1].split('_')
            method = method_action[0]
            if len(method_action) < 2:
                action = method
            else:
                action = method_action[1]
            parm = pattern.findall(r['rule'])
            if parm:
                parm = parm[0][2]
            else:
                parm = None
            url = pattern.sub("", r['rule'])
            res = {
                "name": name,
                "action": action,
                "method": method,
                "require_login": False,
                "url": url,
                "parm": parm
            }
            res_list.append(res)

    return res_list