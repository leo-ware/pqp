
def recursive_sort(d):
    if isinstance(d, dict):
        return {k: recursive_sort(v) for k, v in sorted(d.items())}
    elif isinstance(d, list):
        return list(sorted(recursive_sort(v) for v in d))
    elif isinstance(d, tuple):
        return tuple(sorted(recursive_sort(v) for v in d))
    else:
        return d