from expression import parse_json
import backend
import json
import networkx as nx

class Graph:
    def __init__(self, edges):
        self.bi_edges = []
        self.directed_edges = []
        for edge in edges:
            self.add_edge(edge)
    
    def add_edge(self, edge):
        if isinstance(edge, BidirectedEdge):
            self.bi_edges.append(edge)
        elif isinstance(edge, DirectedEdge):
            self.directed_edges.append(edge)
        else:
            raise TypeError(f"Cannot add edge of type {type(edge)}")
    
    def bi_edge_tuples(self):
        return [(str(edge.a), str(edge.b)) for edge in self.bi_edges]
    
    def di_edge_tuples(self):
        return [(str(edge.start), str(edge.end)) for edge in self.directed_edges]
    
    def idc(self, x, y, z=[]):
        res = backend.id(
            self.di_edge_tuples(),
            self.bi_edge_tuples(),
            [str(v) for v in x],
            [str(v) for v in y],
            [str(v) for v in z],
        )
        return parse_json(json.loads(res))
    
    def draw(self):
        layout_graph = nx.Graph()
        layout_graph.add_edges_from(self.bi_edge_tuples() + self.di_edge_tuples())
        layout = nx.spring_layout(layout_graph, scale=1, k=1/len(layout_graph.nodes)**0.5)
        nx.draw_networkx_nodes(layout_graph, layout, node_size=500)

        digraph = nx.DiGraph()
        digraph.add_edges_from(self.di_edge_tuples())
        nx.draw_networkx_edges(digraph, layout)

        bigraph = nx.Graph()
        bigraph.add_edges_from(self.bi_edge_tuples())
        nx.draw_networkx_edges(bigraph, layout, style="dashed")

        nx.draw_networkx_labels(layout_graph, layout)
    
    def __repr__(self):
        return f"Graph({self.edges})"
    
    def __str__(self):
        return f"Graph({self.edges})"

class DirectedEdge:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __repr__(self):
        return f"DirectedEdge({self.start}, {self.end})"
    
    def __str__(self):
        return f"{self.end} <= {self.start}"

class BidirectedEdge:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __repr__(self):
        return f"BidirectedEdge({self.a}, {self.b})"
    
    def __str__(self):
        return f"{self.a} & {self.b}"

class Variable:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"
    
    def __str__(self):
        return self.name
    
    def __le__(self, other):
        if isinstance(other, Variable):
            return DirectedEdge(other, self)
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
    
    def __and__(self, other):
        if isinstance(other, Variable):
            return BidirectedEdge(self, other)
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

def vars(names):
    return [Variable(name) for name in names]