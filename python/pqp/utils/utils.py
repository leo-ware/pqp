
def recursive_sort(d):
    if isinstance(d, dict):
        return {k: recursive_sort(v) for k, v in sorted(d.items())}
    elif isinstance(d, list):
        return list(sorted(recursive_sort(v) for v in d))
    elif isinstance(d, tuple):
        return tuple(sorted(recursive_sort(v) for v in d))
    else:
        return d

class attrdict(dict):
    def __getattr__(self, key):
        return self[key]

class staticproperty(staticmethod):
    def __get__(self, *_):         
        return self.__func__()
