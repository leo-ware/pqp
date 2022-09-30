use std::fmt::Debug;
use super::{
    Graph,
    Node,
    graph::{BiGraph, DiGraph},
    Map,
    Set,
};

#[derive(Debug)]
pub struct GraphBuilder<'a> {
    pub nodes: Set<Node<'a>>,
    pub edges: Map<Node<'a>, Set<Node<'a>>>
}

impl<'a> GraphBuilder<'a> {
    pub fn new () -> GraphBuilder<'a> {
        return GraphBuilder {
            edges: Map::new(),
            nodes: Set::new(),
        };
    }

    pub fn add_node(&mut self, node: Node<'a>) {
        self.nodes.insert(node);
    }

    pub fn add_edge (&mut self, from: Node<'a>, to: Node<'a>) {
        self.nodes.extend([from, to]);
        self.edges.entry(from).or_insert(Set::new());
        self.edges.entry(from).and_modify(|s| {s.insert(to);});
    }

    pub fn get_nodes (&self) -> &Set<Node> {
        &self.nodes
    }

    pub fn get_edges (&self) -> &Map<Node<'a>, Set<Node<'a>>> {
        &self.edges
    }

    pub fn to_digraph (builder: GraphBuilder) -> DiGraph {
        DiGraph::from_elems(builder.edges, builder.nodes)
    }

    pub fn to_bigraph (builder: GraphBuilder) -> BiGraph {
        let mut edges = builder.edges.to_owned();
        for (from, to) in builder.edges.iter() {
            for target in to {
                edges.entry(*target).or_insert(Set::new());
                edges.entry(*target).and_modify(|b| {b.insert(from);});
            }
        }
        BiGraph::from_elems(edges, builder.nodes)
    }
}
