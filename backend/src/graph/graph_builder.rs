use std::fmt::Debug;
use super::{
    Constructable,
    Node,
    BiGraph,
    DiGraph,
    Map,
    Set, Graph,
};

#[derive(Debug, Clone)]
pub struct GraphBuilder {
    pub nodes: Set<Node>,
    pub edges: Map<Node, Set<Node>>
}

impl GraphBuilder {
    pub fn new () -> GraphBuilder {
        return GraphBuilder {
            edges: Map::new(),
            nodes: Set::new(),
        };
    }

    pub fn from_edges(edges: Vec<(Node, Node)>) -> GraphBuilder {
        let mut gb = GraphBuilder::new();
        for (a, b) in edges {
            gb.add_edge(a, b);
        }
        return gb;
    }

    pub fn from_edges_nodes(edges: Vec<(Node, Node)>, nodes: Vec<Node>) -> GraphBuilder {
        let mut gb = GraphBuilder::from_edges(edges);
        for n in nodes {
            gb.add_node(n);
        }
        return gb;
    }

    pub fn add_node(&mut self, node: Node) {
        self.nodes.insert(node);
    }

    pub fn add_edge(&mut self, from: Node, to: Node) {
        self.nodes.extend([from, to]);
        self.edges.entry(from).or_insert(Set::new());
        self.edges.entry(from).and_modify(|s| {s.insert(to);});
    }

    pub fn get_nodes(&self) -> Set<Node> {
        let mut new = Set::new();
        for node in self.nodes.iter() {
            new.insert(*node);
        }
        return new;
    }

    pub fn get_edges (&self) -> &Map<Node, Set<Node>> {
        &self.edges
    }

    pub fn to_digraph (builder: GraphBuilder) -> DiGraph {
        DiGraph::from_elems(builder.edges, builder.nodes)
    }

    pub fn to_bigraph<'a>(builder: GraphBuilder) -> BiGraph {
        let mut edges: Map<Node, Set<Node>> = Map::new();
        for (from, to) in builder.edges.iter() {
            edges.entry(*from).or_insert(Set::new());
            for target in to {
                edges.entry(*target).or_insert(Set::new());
                edges.entry(*from).and_modify(|b| {b.insert(*target);});
                edges.entry(*target).and_modify(|b| {b.insert(*from);});
            }
        }
        BiGraph::from_elems(edges, builder.nodes)
    }
}
