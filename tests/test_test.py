# coding:utf-8


def fn(a, b):
    return a + b


def test_fn():
    assert fn(1, 2) == 3


class TestClass:

    def test_one(self):
        x = "this"
        assert 'h' in x

    def test_two(self):
        self.x = "hello"
        assert hasattr(self, 'x')
