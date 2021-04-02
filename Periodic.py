import time
from functools import wraps


def periodic_func(duration):
    def _(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            while True:
                fn(*args, **kwargs)
                time.sleep(duration)

        return inner

    return _
