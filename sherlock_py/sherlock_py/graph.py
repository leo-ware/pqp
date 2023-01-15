from sherlock_py.expression import parse_json
import backend
import json

class Graph:
    """A causal graph
    
    Example:
        >>> x = Variable("X")
        >>> y = Variable("Y")
        >>> g = Graph([
        ...     x <= y,
        ...     x & y,
        ... ])
        >>> g.idc([x], [y])
        FAIL
    
    Args:
        edges (list of DirectedEdge or BidirectedEdge): the edges in the graph
    """
    def __init__(self, edges=[]):
        self.bi_edges = []
        self.directed_edges = []
        for edge in edges:
            self.add_edge(edge)
    
    def add_edge(self, edge):
        """Adds an edge to the graph
        
        Args:
            edge (DirectedEdge or BidirectedEdge): the edge to add
        """
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
        """Identification of conditional interventional distribution.

        Args:
            x (list of Variable): intervention variables
            y (list of Variable): outcome variables
            z (list of Variable): conditioning variables (optional)
        
        Returns:
            Expression: the expression for the interventional distribution
        """
        res = backend.id(
            self.di_edge_tuples(),
            self.bi_edge_tuples(),
            [str(v) for v in x],
            [str(v) for v in y],
            [str(v) for v in z],
        )
        return parse_json(json.loads(res))
    
    def draw(self):
        """Draws the causal diagram using networkx"""
        import networkx as nx

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
    """A directed edge between two variables, represents a causal relationship
    
    Args:
        start (Variable): the start of the edge
        end (Variable): the end of the edge
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __repr__(self):
        return f"DirectedEdge({self.start}, {self.end})"
    
    def __str__(self):
        return f"{self.end} <= {self.start}"

class BidirectedEdge:
    """A bidirected edge between two variables, represents confounding in the causal model
    
    Args:
        a (Variable): one of the variables
        b (Variable): the other variable
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __repr__(self):
        return f"BidirectedEdge({self.a}, {self.b})"
    
    def __str__(self):
        return f"{self.a} & {self.b}"

class Variable:
    """A variable in the causal model
    
    Dunder methods allow for convenient syntax for creating causal graphs.

    Example:
        >>> x = Variable("x")
        >>> y = Variable("y")
        >>> x <= y
        DirectedEdge(Variable("x"), Variable("y"))
        >>> x & y
        BidirectedEdge(Variable("x"), Variable("y"))
    
    Args:
        name (str): the name of the variable
    """
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

def make_vars(names):
    """Creates a list of variables from a list of names
    
    Example:
        >>> make_vars(["x", "y", "z"])
        [Variable("x"), Variable("y"), Variable("z")]
    
    """
    return [Variable(name) for name in names]