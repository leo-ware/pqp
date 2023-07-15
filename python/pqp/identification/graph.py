from pqp.symbols import Variable, Expectation, parse_json, P, EqualityEvent, InterventionEvent, do
from pqp.identification.estimands import ATE, CATE, AbstractCausalEstimand, CausalEstimand
from pqp.refutation import entrypoint, Result
from pqp.pqp import id as rust_id

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Any
import json
from itertools import chain

class IdentificationResult(Result):
    """Stores the result of identification

    Attributes:
        identified_estimand (AbstractExpression): the identified causal estimand
    """
    _keys = ["identified_estimand"]


@dataclass(frozen=True)
class SearchNode:
    prev: Optional["SearchNode"]
    graph_node: Any

    def unpack(self, _path=None):
        if _path is None:
            p = []
            self.unpack(_path=p)
            return list(reversed(p))
        
        _path.append(self.graph_node)
        if self.prev is not None:
            self.prev.unpack(_path=_path)


class Graph:
    """A causal graph

    The best way to create a `Graph` is using the `<=` and `&` infix operators. When you use
    these operators between `Variable`s, they create a `DirectedEdge` or `BidirectedEdge` respectively.

    Example: The Front-Door Model
        >>> x, y, m = make_vars("xym")
        >>> g = Graph([
        ...     m <= x,
        ...     y <= m,
        ...     y & x,
        ... ])
    
    Example: The Back-Door Model
        >>> x, y, z = make_vars("xyz")
        >>> g = Graph([
        ...     y <= [x, z],
        ...     x <= z,
        ... ])

    You can use the `identify` method to identify a causal estimand. The estimand can either
    be passed as an expression or as an instance of `AbstractCausalEstimand`, such as `ATE` or
    `CATE`.

    Example:
        >>> x = Variable("X")
        >>> y = Variable("Y")
        >>> g = Graph([
        ...     y <= x,
        ... ])
        >>> g.identify(ATE([y], [x]))
        P(y | x)
    
    Args:
        edges (list of DirectedEdge or BidirectedEdge): the edges in the graph
    """
    def __init__(self, edges=[]):
        self.bi_edges = []
        self.directed_edges = []
        self.nodes = set()
        self.add_edges(edges)
    
    def add_node(self, node):
        """Adds a node to the graph
        
        Args:
            node (Variable): the node to add
        """
        self.nodes.add(node)
    
    def add_nodes(self, nodes):
        """Adds multiple nodes to the graph
        
        Args:
            nodes (list of Variable): the nodes to add
        """
        self.nodes.update(nodes)
    
    def add_edges(self, edges):
        """Add multiple edges to the graph
        
        Args:
            edges (list of DirectedEdge or BidirectedEdge): the edges to add
        """
        while edges:
            edge = edges.pop()
            if isinstance(edge, BidirectedEdge) or isinstance(edge, DirectedEdge):
                self.add_edge(edge)
            elif isinstance(edge, list):
                edges.extend(edge)
            else:
                raise TypeError(f"Cannot add edge of type {type(edge)}")
    
    def add_edge(self, edge):
        """Adds an edge to the graph
        
        Args:
            edge (DirectedEdge or BidirectedEdge): the edge to add
        """
        if isinstance(edge, BidirectedEdge):
            self.bi_edges.append(edge)
            self.add_nodes([edge.a, edge.b])
        elif isinstance(edge, DirectedEdge):
            self.directed_edges.append(edge)
            self.add_nodes([edge.start, edge.end])
        else:
            raise TypeError(f"Cannot add edge of type {type(edge)}")
    
    def _bi_edge_tuples(self):
        return [(str(edge.a), str(edge.b)) for edge in self.bi_edges]
    
    def _di_edge_tuples(self):
        return [(str(edge.start), str(edge.end)) for edge in self.directed_edges]
    
    def _idc(self, y, x, z=[], step=None):
        """Identification of conditional interventional distribution.

        Args:
            x (list of Variable): intervention variables
            y (list of Variable): outcome variables
            z (list of Variable): conditioning variables (optional)
        
        Returns:
            AbstractExpression: the expression for the interventional distribution
        """
        
        def purify_vars(vs):
            for v in vs:
                if isinstance(v, Variable):
                    yield v
                elif isinstance(v, str):
                    yield Variable(v)
                else:
                    raise TypeError(f"Cannot convert {type(v)} to Variable")

        y = list(purify_vars(y))
        x = list(purify_vars(x))
        z = list(purify_vars(z))

        res = rust_id(
            self._di_edge_tuples(),
            self._bi_edge_tuples(),
            [str(v) for v in x],
            [str(v) for v in y],
            [str(v) for v in z],
        )
        res_exp = parse_json(json.loads(res))
        
        if step:
            step = step.substep("IDC")
            step.write("Input:")
            step.write(P(y, given=z + [do(v) for v in x]))
            step.write("Output:")
            step.write(res_exp)
            # step.result("identified_expression", str(res_exp))
        
        return res_exp
    
    @entrypoint("Identification", result_class=IdentificationResult)
    def identify(self, estimand, step):
        """Uses IDC to identify an arbitrary estimand

        Finds the interventional distributions in a causal estimand and replaces
        them with equivalent conditional probability expressions using IDC.

        Args:
            estimand (Expression): the estimand to identify
        
        Returns:
            AbstractExpression: the identified estimand, containing no do-operators
        """
        if isinstance(estimand, AbstractCausalEstimand):
            causal_estimand = estimand
            estimand = estimand.expression()
        else:
            causal_estimand = CausalEstimand(exp=estimand)
        
        step.write(f"We will identify the {causal_estimand.name} using IDC.")
        step.assume("Noncontradictory evidence")
        step.assume("Acyclicity")
        step.assume("Positivty")

        _idc_cache = {}
        def idc_caller(y, x, z=[]):
            key = (tuple(y), tuple(x), tuple(z))
            if key not in _idc_cache:
                _idc_cache[key] = self._idc(y, x, z, step=step)
            return _idc_cache[key]

        def id(exp):
            if isinstance(exp, P):
                intervene = exp.get_intervened_vars()
                condition = exp.get_conditioned_vars()
                measured = exp.get_vars()

                if len(intervene) == 0:
                    return exp.copy()
                
                transformed = idc_caller(
                    y=list(measured.keys()),
                    x=list(intervene.keys()),
                    z=list(condition.keys()),
                    )
                
                for var, val in chain(condition.items(), intervene.items(), measured.items()):
                    transformed = transformed.assign(var, val)
                
                return transformed
            else:
                return exp.copy()
        
        ans = estimand.r_map(id)
        step.result("identified_estimand", ans)
    
    def identify_ate(self, outcome, treatment_condition, control_condition):
        """Identifies the average treatment effect

        Args:
            outcome (Variable): the outcome variable
            treatment_condition (dict): the treatment condition
            control_condition (dict): the control condition
        
        Returns:
            AbstractExpression: the identified average treatment effect
        """
        return self.identify(ATE(outcome, treatment_condition, control_condition).expression())
    
    def identify_cate(self, outcome, treatment_condition, control_condition, subpopulation):
        """Identifies the conditional average treatment effect

        Args:
            outcome (Variable): the outcome variable
            treatment_condition (dict): the treatment condition
            control_condition (dict): the control condition
            subpopulation (dict): the subpopulation condition
        
        Returns:
            AbstractExpression: the identified conditional average treatment effect
        """
        return self.identify(CATE(outcome, treatment_condition, control_condition, subpopulation).expression())
    
    def draw(self):
        """Draws the causal diagram using networkx"""
        import networkx as nx

        layout_graph = nx.Graph()
        layout_graph.add_edges_from(self._bi_edge_tuples() + self._di_edge_tuples())
        layout = nx.spring_layout(layout_graph, scale=1, k=1/len(layout_graph.nodes)**0.5)
        nx.draw_networkx_nodes(layout_graph, layout, node_size=500)

        digraph = nx.DiGraph()
        digraph.add_edges_from(self._di_edge_tuples())
        nx.draw_networkx_edges(digraph, layout)

        bigraph = nx.Graph()
        bigraph.add_edges_from(self._bi_edge_tuples())
        nx.draw_networkx_edges(bigraph, layout, style="dashed")

        nx.draw_networkx_labels(layout_graph, layout)
    
    def __repr__(self):
        return f"Graph({self.bi_edges + self.directed_edges})"
    
    def __str__(self):
        return f"<Graph n_edges={len(self.bi_edges + self.directed_edges)}>"
    
    def dir_edge_dict(self):
        """Returns a dict mapping each node to its children in the graph"""
        edges = defaultdict(list)
        for edge in self.directed_edges:
            edges[edge.start].append(edge.end)
        return dict(edges)
    
    def _dfs(self, start, end):
        if start == end:
            yield [start]
        else:
            edges = self.dir_edge_dict()
            stack = [SearchNode(None, start)]
            while stack:
                node = stack.pop()
                for nxt in edges.get(node.graph_node, []):
                    nxt_node = SearchNode(node, nxt)
                    if nxt == end:
                        yield nxt_node.unpack()
                    else:
                        stack.append(nxt_node)
    
    def dfs(self, start, end):
        """Performs a depth-first search over directed edges in the graph, returning a generator over paths
        
        Args:
            start (Variable): the start of the search
            end (Variable): the end of the search
        
        Returns:
            Generator[List[DirectedEdge]]: the path from start to end
        """
        if start not in self.nodes:
            raise ValueError(f"{start} is not in the graph")
        if end not in self.nodes:
            raise ValueError(f"{end} is not in the graph")
        return self._dfs(start, end)

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
        return f"DirectedEdge(start={self.start}, end={self.end})"
    
    def __str__(self):
        return f"{self.end} <= {self.start}"
    
    def __eq__(self, other):
        return (isinstance(other, DirectedEdge) and
                self.start == other.start and
                self.end == other.end)
    
    def __le__(self, other):
        if isinstance(other, Variable):
            return [self, self.start <= other]
        elif isinstance(other, DirectedEdge):
            return [self, self.start <= other.end, other]
        elif isinstance(other, BidirectedEdge):
            return [self, self.start <= other.a, other]
        elif isinstance(other, list):
            return [self] + [self <= o for o in other]
        else:
            raise TypeError(f"Cannot add edge of type {type(other)}")

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
    
    def __eq__(self, other):
        return isinstance(other, BidirectedEdge) and (
            (self.a == other.a and self.b == other.b) or
            (self.a == other.b and self.b == other.a)
        )

    def __le__(self, other):
        if isinstance(other, Variable):
            return [self, self.b & other]
        elif isinstance(other, DirectedEdge):
            return [self, self.b & other.end, other]
        elif isinstance(other, BidirectedEdge):
            return [self, self.b & other.a, other]
        elif isinstance(other, list):
            return [self] + [self & o for o in other]
        else:
            raise TypeError(f"Cannot add edge of type {type(other)}")
