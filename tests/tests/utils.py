import contextlib

@contextlib.contextmanager
def fake_sub_test(**kwrags):
    yield
