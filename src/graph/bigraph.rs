use super::{Graph, Constructable, Set, Map, Node, GraphBuilder};
use std::rc::Rc;
use crate::utils::set_utils::{union, difference};

#[derive(Debug, Clone)]
pub struct BiGraph {
    edges: Rc<Map<Node, Set<Node>>>,
    nodes: Box<Set<Node>>,
}

impl Constructable for BiGraph {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self {
        BiGraph {
            edges: Rc::new(edges),
            nodes: Box::new(nodes),
        }
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