use super::{Graph, Constructable, Set, Map, Node, GraphBuilder};
use std::rc::Rc;
use crate::set_utils::union;

#[derive(Debug)]
pub struct BiGraph {
    edges: Rc<Map<Node, Set<Node>>>,
    nodes: Box<Set<Node>>,
    orphans: Box<Set<Node>>,
}

impl Constructable for BiGraph {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self {
        BiGraph {
            edges: Rc::new(edges),
            nodes: Box::new(nodes),
            orphans: Box::new(Set::new())
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
            orphans: self.orphans.clone()
        }
    }

    fn r#do(&self, nodes: &Set<Node>) -> Self {
        BiGraph {
            edges: self.edges.clone(),
            nodes: self.nodes.clone(),
            orphans: Box::new(union(&*self.orphans, nodes))
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

    fn get_component (&self, node: Node) -> Set<Node> {
        let mut acc = Set::new();
        let mut queue = Vec::from([node]);
        loop {
            match queue.pop() {
                None => break,
                Some(node) => {
                    if acc.insert(node) {
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
        let mut unvisited: Set<Node> = self.nodes.iter().map(|e| *e).collect();
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