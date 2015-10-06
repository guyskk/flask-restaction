from flask_restaction import Permission


def test_permission():
    p = Permission(filepath="tests/test_permission.json")
    assert p.permit("admin", "photo", "get")
    assert p.permit("userA", "photo", "get")
    assert not p.permit("userA", "message", "Post")
    assert not p.permit("userA", "message", "delete")
    assert p.permit("userB", "photo", "get_list")
    assert not p.permit("userB", "photo", "get")
    assert p.permit("userB", "message", "post")
    assert not p.permit("userB", "message", "delete")
    assert p.permit("userXX", "photo", "get")
    assert not p.permit("userXX", "photo", "delete")


def test_permission2():
    p = Permission(jsonstr="{}")
    p.add("admin", "*", "get")
    p.add("admin", "photo", "post")
    p.add("userA", "photo*", "get")
    p.add("userA", "photo", "get_list")
    p.add("userB", "photo", "get_list")
    p.add("userB", "photo", "post")
    assert p.permit("admin", "message", "get")
    assert p.permit("admin", "photo", "get")
    assert p.permit("userA", "photo", "get")
    assert p.permit("userA", "photo", "Post")
    assert not p.permit("userA", "message", "delete")
    assert p.permit("userB", "photo", "get_list")
    assert p.permit("userB", "photo", "post")
    assert not p.permit("userXX", "photo", "get")
    assert not p.permit("userXX", "photo", "delete")
    p.remove("userB", "photo", "post")
    p.remove("userB", "photo", "delete")
    assert not p.permit("userB", "message", "post")
    assert not p.permit("userB", "message", "delete")
