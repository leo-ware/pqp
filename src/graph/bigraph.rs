use super::{Graph, ConcreteGraph, Set, Map, Node, GraphBuilder};
use std::{
    rc::Rc,
    collections::BTreeMap,
};
use crate::{utils::set_utils::{union, difference}, model::serialize::{Serializable, recover_graph, write_graph}};
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone)]
pub struct BiGraph {
    edges: Rc<Map<Node, Set<Node>>>,
    nodes: Box<Set<Node>>,
}

impl ConcreteGraph for BiGraph {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self {
        BiGraph {
            edges: Rc::new(edges),
            nodes: Box::new(nodes),
        }
    }

    fn get_edges(&self) -> &Map<Node, Set<Node>> {
        &*self.edges
    }
}

impl Graph for BiGraph {
    fn get_nodes(&self) -> &Set<Node> {
        &self.nodes
    }

    fn subgraph(&self, nodes: &Set<Node>) -> Self {
        BiGraph {
            edges: self.edges.clone(),
            nodes: Box::new(nodes.clone()),
        }
    }

    fn r#do(&self, nodes: &Set<Node>) -> Self {
        let mut edges = Map::new();
        for (from, to) in self.edges.iter() {
            if !nodes.contains(from) {
                edges.insert(*from, difference(to, nodes));
            }
        }

        BiGraph {
            edges: Rc::new(edges),
            nodes: self.nodes.clone(),
        }
    }
}

impl Serializable for BiGraph {
    fn to_serde(&self) -> serde_json::Value {
        write_graph(self)
    }

    fn from_serde(v: serde_json::Value) -> Result<Self, String> {
        if let Some((edges, nodes)) = recover_graph(v) {
            Ok(BiGraph::from_elems(edges, nodes))
        } else {
            Err("problem recovering BiGraph".to_string())
        }
    }
}

impl PartialEq for BiGraph {
    fn eq(&self, other: &Self) -> bool {
        if self.nodes != other.nodes {
            return false;
        }

        if self.nodes.len() == 0 {
            return true;
        }

        for c_comp in self.c_components().into_iter() {
            let elem = c_comp.iter().next().unwrap();
            let other_c_comp = other.get_component(*elem);
            if c_comp != other_c_comp {
                return false;
            }
        }

        return true;
    }
}

impl BiGraph {
    pub fn from_edges(edges: Vec<(Node, Node)>) -> BiGraph {
        GraphBuilder::to_bigraph(GraphBuilder::from_edges(edges))
    }

    pub fn from_edges_nodes(edges: Vec<(Node, Node)>, nodes: Vec<Node>) -> BiGraph {
        GraphBuilder::to_bigraph(GraphBuilder::from_edges_nodes(edges, nodes))
    }

    pub fn get_component (&self, node: Node) -> Set<Node> {
        let mut acc = Set::new();
        let mut queue = Vec::from([node]);
        loop {
            match queue.pop() {
                None => break,
                Some(node) => {
                    if self.nodes.contains(&node) && acc.insert(node) {
                        match self.edges.get(&node) {
                            Some(siblings) => queue.extend(siblings),
                            None => {}
                        }
                    }
                }
            }
        }
        return acc;
    }

    pub fn c_components (&self) -> Vec<Set<Node>> {
        let mut unvisited: Set<Node> = self.nodes.iter().cloned().collect();
        let mut components = Vec::new();

        for node in self.nodes.iter() {
            if unvisited.contains(node) {
                let node_component = self.get_component(*node);
                for sibling in node_component.iter() {
                    unvisited.remove(sibling);
                }
                components.push(node_component);
            }
        }

        return components;
    }
}