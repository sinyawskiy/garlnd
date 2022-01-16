from brake.decorators import ratelimit


def garlnd_ratelimit(ip=True, block=False, method=None, field=None, rate='5/m'):
    def decorator(fn):
        def wrapper(self, request, *args, **kwargs):
            @ratelimit(ip, block, method, field, rate)
            def ratelimit_test(request):
                pass
            ratelimit_test(request)
            return fn(self, request, *args, **kwargs)
        return wrapper
    return decorator
