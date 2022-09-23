use std::{
    collections::{HashMap as Map, HashSet as Set},
    iter::FromIterator,
    fmt::Debug,
};

use crate::utils::{set_union, make_set};

pub type Node<'a> = &'a str;

//
// trait definitions
pub trait Graph<'a> where Self: Debug {
    fn new() -> Self;
    fn add_node(&mut self, node: Node<'a>);
    fn add_edge(&mut self, from: Node<'a>, to: Node<'a>);
}

pub trait Subgraph<'a, T: Subgraph<'a, T>> where Self: Sized + Debug {
    fn subgraph(&'a self, nodes: &impl Iterator<Item=&'a str>) -> T;
    fn r#do(&'a self, nodes: &impl Iterator<Item=&'a str>) -> T;
}

//
// digraph
#[derive(Debug)]
pub struct DiGraph<'a> {
    nodes: Set<Node<'a>>,
    edges: Map<Node<'a>, Set<Node<'a>>>
}

impl<'a> Graph<'a> for DiGraph<'a> {
    fn new () -> DiGraph<'a> {
        return DiGraph {
            edges: Map::new(),
            nodes: Set::new(),
        };
    }

    fn add_node(&mut self, node: Node<'a>) {
        self.nodes.insert(node);
    }

    fn add_edge (&mut self, from: Node<'a>, to: Node<'a>) {
        self.nodes.extend([from, to]);
        self.edges.entry(from).or_insert(Set::new());
        self.edges.entry(from).and_modify(|s| {s.insert(to);});
    }
}

impl<'a> Subgraph<'a, SubDigraph<'a>> for DiGraph<'a> {
    fn subgraph (&'a self, nodes: &impl Iterator<Item=&'a str>) -> SubDigraph<'a> {
        SubDigraph::<'a> { graph: self, nodes: &make_set(nodes), orphans: &Set::new()}
    }

    fn r#do (&'a self, nodes: &impl Iterator<Item=&'a str>) -> SubDigraph<'a> {
        SubDigraph { graph: self, nodes: &self.nodes, orphans: &make_set(nodes) }
    }
}

//
// subdigraph
#[derive(Debug)]
pub struct SubDigraph<'a> {
    graph: &'a DiGraph<'a>,
    nodes: &'a Set<&'a str>,
    orphans: &'a Set<&'a str>,
}

impl<'a> SubDigraph<'a> {
    pub fn parents (&self, x: &'a str) -> Set<&'a str> {
        let empty = Set::new();
        let elems = match self.graph.edges.get(x) {
            Some(kids) => kids,
            None => &empty,
        };
        let filtered = elems.into_iter()
            .filter(|elem| self.nodes.contains(**elem))
            .map(|elem| *elem);
        return Set::from_iter(filtered);
    }

    pub fn ancestors (&self, x: &'a str) -> Set<&'a str> {
        self.ancestors_set(&Set::from([x]))
    }

    pub fn ancestors_set (&self, x: &Set<&'a str>) -> Set<&'a str> {
        let mut acc = Set::new();
        let mut queue = Vec::new();
        queue.extend(x);
        
        for _ in 0..(self.nodes.len() + 1) {
            match queue.pop() {
                Some(elem) => {
                    for parent in self.parents(elem) {
                        if self.nodes.contains(parent) {
                            acc.insert(parent);
                            if !self.orphans.contains(parent) {
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

    pub fn root_set(&self) -> Vec<&'a str> {
        return self.count_parents().iter()
            .filter(|(k, v)| **v == 0)
            .map(|(k, _)| *k)
            .collect();
    }

    pub fn count_parents(&self) -> Map<&'a str, i32> {
        let mut n_parents: Map<&str, i32> = Map::new();
        for x in self.nodes {
            n_parents.insert(x, 0);
        }

        for x in self.nodes {
            for p in self.parents(x) {
                n_parents.entry(p).and_modify(|e| {*e += 1});
            }
        }

        return n_parents;
    }

    pub fn order(&self) -> Vec<&'a str> {
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
                        if n_parents[p] == 0 {
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

impl<'a> Subgraph<'a, SubDigraph<'a>> for SubDigraph<'a> {
    fn subgraph(&self, nodes: &impl Iterator<Item=&'a str>) -> SubDigraph<'a> {
        SubDigraph { graph: self.graph, nodes: &make_set(nodes), orphans: self.orphans }
    }

    fn r#do(&self, nodes: &impl Iterator<Item=&'a str>) -> Self {
        SubDigraph { graph: self.graph, nodes: self.nodes, orphans: &set_union(self.orphans, &make_set(nodes)) }
    }
}

// //
// // undirected graph
// pub struct BiGraph {
//     nodes: 
// }