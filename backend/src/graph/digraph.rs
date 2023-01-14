use crate::{utils::set_utils::{difference, make_set}, set};

use super::{Graph, Constructable, Set, Map, Node, GraphBuilder};
use std::rc::Rc;

#[derive(Debug, Clone)]
pub struct DiGraph {
    edges: Rc<Map<Node, Set<Node>>>,
    nodes: Box<Set<Node>>,
}

impl DiGraph {
    pub fn from_edges (edges: Vec<(Node, Node)>) -> DiGraph {
        GraphBuilder::to_digraph(GraphBuilder::from_edges(edges))
    }

    pub fn from_edges_nodes(edges: Vec<(Node, Node)>, nodes: Vec<Node>) -> DiGraph {
        GraphBuilder::to_digraph(GraphBuilder::from_edges_nodes(edges, nodes))
    }

    pub fn children(&self, x: &Node) -> Set<Node> {
        let mut acc = set![];
        for (k, v) in self.edges.iter() {
            if self.nodes.contains(&k) && v.contains(x) {
                acc.insert(*k);
            }
        }
        return acc;
    }

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

    // TODO: by default, x should be considered a subset of ancestors of x
    // otherwise semantics too tricky when one element in set is ancestor of another
    pub fn ancestors_set (&self, x: &Set<Node>) -> Set<Node> {
        if !x.is_subset(&self.nodes) {
            panic!("cannot find ancestors of {:?} in DiGraph {:?} because not all queried
                nodes were found in the graph", x, self);
        }

        let mut acc = make_set(x.iter().cloned());
        let mut queue = Vec::new();
        queue.extend(x);
        
        for _ in 0..(self.nodes.len() + 1) {
            match queue.pop() {
                Some(elem) => {
                    for parent in self.parents(elem) {
                        if self.nodes.contains(&parent) {
                            if acc.insert(parent) {
                                queue.push(parent);
                            }
                        }
                    }
                },
                None => {
                    // TODO this is awkward
                    for val in x {
                        acc.remove(val);
                    }
                    return acc;
                },
            }
        }

        panic!("infinite loop detected: cannot find ancestors of {:?} in DiGraph {:?}",
            x, self);
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
        }
    }

    fn r#do(&self, nodes: &Set<Node>) -> Self {
        let mut edges = Map::new();
        for (from, to) in self.edges.iter() {
            if !nodes.contains(from) {
                edges.insert(*from, to.clone());
            }
        }

        DiGraph {
            edges: Rc::new(edges),
            nodes: self.nodes.clone(),
        }
    }
}