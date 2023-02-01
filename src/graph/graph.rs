use super::{Node, Map, Set, GraphBuilder};

pub trait Graph {
    fn subgraph(&self, nodes: &Set<Node>) -> Self;
    fn r#do(&self, nodes: &Set<Node>) -> Self;
    fn get_nodes(&self) -> &Set<Node>;
}

pub trait Constructable {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self;
}