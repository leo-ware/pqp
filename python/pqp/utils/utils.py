from collections import defaultdict


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

def order_graph(g):
    """
    Takes a graph (as dict from el to list of elem) and returns a list of elements
    such that for each edge (a, b) in the graph, a comes before b in the list
    """
    incoming_counts = {}
    for k, v in g.items():
        for i in [k] + v:
            incoming_counts[i] = 0
    for k, v in g.items():
        for el in v:
            incoming_counts[el] += 1
    n = len(incoming_counts.keys())

    if n == 0:
        return []
    
    ls = []
    for _ in range(n + 1):
        for k, v in list(incoming_counts.items()):
            if v == 0:
                del incoming_counts[k]
                n -= 1
                ls.append(k)
                if k in g:
                    for el in g[k]:
                        if el in incoming_counts:
                            incoming_counts[el] -= 1
            if not n:
                return ls
    raise Exception("Cycle detected")
