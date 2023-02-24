use crate::model::serialize::Serializable;

use super::{Node, Map, Set, GraphBuilder};

use std::rc::Rc;
use serde_json::{Result, Value};


pub trait Graph: Serializable {
    fn subgraph(&self, nodes: &Set<Node>) -> Self;
    fn r#do(&self, nodes: &Set<Node>) -> Self;
    fn get_nodes(&self) -> &Set<Node>;
}

pub trait ConcreteGraph: Graph {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self;
    fn get_edges(&self) -> &Map<Node, Set<Node>>;
}