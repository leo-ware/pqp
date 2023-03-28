from pqp.symbols import Variable, Expectation, parse_json, P, EqualityEvent, InterventionEvent, do
from pqp.identification.estimands import ATE, CATE, AbstractCausalEstimand, CausalEstimand
from pqp.refutation import entrypoint
from pqp.pqp import id as rust_id
import json
from itertools import chain

class Graph:
    """A causal graph
    
    Example:
        >>> x = Variable("X")
        >>> y = Variable("Y")
        >>> g = Graph([
        ...     y <= x,
        ... ])
        >>> g.idc([y], [x])
        P(y | x)
    
    Args:
        edges (list of DirectedEdge or BidirectedEdge): the edges in the graph
    """
    def __init__(self, edges=[]):
        self.bi_edges = []
        self.directed_edges = []
        self.add_edges(edges)
    
    def add_edges(self, edges):
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
        elif isinstance(edge, DirectedEdge):
            self.directed_edges.append(edge)
        else:
            raise TypeError(f"Cannot add edge of type {type(edge)}")
    
    def bi_edge_tuples(self):
        return [(str(edge.a), str(edge.b)) for edge in self.bi_edges]
    
    def di_edge_tuples(self):
        return [(str(edge.start), str(edge.end)) for edge in self.directed_edges]
    
    def _idc(self, y, x, z=[], step=None):
        """Identification of conditional interventional distribution.

        Args:
            x (list of Variable): intervention variables
            y (list of Variable): outcome variables
            z (list of Variable): conditioning variables (optional)
        
        Returns:
            Expression: the expression for the interventional distribution
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
            self.di_edge_tuples(),
            self.bi_edge_tuples(),
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
            step.result("identified_expression", str(res_exp))
        
        return res_exp
    
    @entrypoint("Identification")
    def identify(self, estimand, step):
        """Uses IDC to identify an arbitrary estimand

        Finds the interventional distributions in a causal estimand and replaces
        them with equivalent conditional probability expressions using IDC.

        Args:
            estimand (Expression): the estimand to identify
        
        Returns:
            Expression: the identified estimand, containing no do-operators
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
            Expression: the identified average treatment effect
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
            Expression: the identified conditional average treatment effect
        """
        return self.identify(CATE(outcome, treatment_condition, control_condition, subpopulation).expression())
    
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
        return f"Graph({self.bi_edges + self.directed_edges})"
    
    def __str__(self):
        return f"<Graph n_edges={len(self.bi_edges + self.directed_edges)}>"


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
