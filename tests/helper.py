import json


def resp_json(resp):
    return json.loads(resp.data.decode("utf-8"))
