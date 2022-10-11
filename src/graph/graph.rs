use std::{
    iter::FromIterator,
    fmt::Debug,
    rc::Rc,
};

use crate::set_utils::union;

use super::{Node, Map, Set};

pub trait Graph {
    fn subgraph(&self, nodes: &Set<Node>) -> Self;
    fn r#do(&self, nodes: &Set<Node>) -> Self;
    fn get_nodes(&self) -> &Set<Node>;
}

pub trait Constructable {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self;
}

#[derive(Debug)]
pub struct DiGraph {
    edges: Rc<Map<Node, Set<Node>>>,
    nodes: Box<Set<Node>>,
    orphans: Box<Set<Node>>,
}

impl DiGraph {
    pub fn parents (&self, x: Node) -> Set<Node> {
        let empty = Set::new();
        let elems = match self.edges.get(&x) {
            Some(kids) => kids,
            None => &empty,
        };
        let filtered = elems.into_iter()
            .filter(|elem| self.nodes.contains(*elem))
            .map(|elem| *elem);
        return Set::from_iter(filtered);
    }

    pub fn ancestors (&self, x: Node) -> Set<Node> {
        self.ancestors_set(&Set::from([x]))
    }

    pub fn ancestors_set (&self, x: &Set<Node>) -> Set<Node> {
        let mut acc = Set::new();
        let mut queue = Vec::new();
        queue.extend(x);
        
        for _ in 0..(self.nodes.len() + 1) {
            match queue.pop() {
                Some(elem) => {
                    for parent in self.parents(elem) {
                        if self.nodes.contains(&parent) {
                            acc.insert(parent);
                            if !self.orphans.contains(&parent) {
                                queue.push(parent);
                            }
                        }
                    }
                },
                None => return acc,
            }
        }

        panic!("infinite loop detected");
    }

    pub fn root_set(&self) -> Vec<Node> {
        return self.count_parents().iter()
            .filter(|(_, v)| **v == 0)
            .map(|(k, _)| *k)
            .collect();
    }

    pub fn count_parents(&self) -> Map<Node, i32> {
        let mut n_parents: Map<Node, i32> = Map::new();
        for x in self.nodes.iter() {
            n_parents.insert(*x, 0);
        }

        for x in self.nodes.iter() {
            for p in self.parents(*x) {
                n_parents.entry(p).and_modify(|e| {*e += 1});
            }
        }

        return n_parents;
    }

    pub fn order(&self) -> Vec<Node> {
        let mut n_parents = self.count_parents();
        let mut lst = vec![];
        let mut queue = vec![];
        for (k, v) in n_parents.iter() {
            if *v == 0 {
                lst.push(*k);
                queue.push(*k);
            }
        }

        loop {
            match queue.pop() {
                Some(x) => {
                    for p in self.parents(x) {
                        n_parents.entry(p).and_modify(|e| *e -= 1);
                        if n_parents[&p] == 0 {
                            queue.push(p);
                            lst.push(p);
                        }
                    }
                },
                None => break
            }
        }

        return lst;
    }

}

impl Constructable for DiGraph {
    fn from_elems(edges: Map<Node, Set<Node>>, nodes: Set<Node>) -> Self {
        DiGraph {
            edges: Rc::new(edges),
            nodes: Box::new(nodes),
            orphans: Box::new(Set::new())
        }
    }
}

impl Graph for DiGraph {
    fn get_nodes(&self) -> &Set<Node> {
        &*self.nodes
        // yo mama so ugly
    }

    fn subgraph(&self, nodes: &Set<Node>) -> Self {
        DiGraph {
            edges: Rc::clone(&self.edges),
            nodes: Box::new(nodes.clone()),
            orphans: self.orphans.clone()
        }
    }

    fn r#do(&self, nodes: &Set<Node>) -> Self {
        DiGraph {
            edges: Rc::clone(&self.edges),
            nodes: self.nodes.clone(),
            orphans: Box::new(union(&*self.orphans, nodes))
        }
    }
}

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