use std::{
    iter::FromIterator,
    fmt::Debug,
    rc::Rc,
};

use crate::utils::{set_union, make_set};

use super::{Node, Map, Set};

pub trait Graph<'a> where Self: Sized + Debug {
    fn from_elems(edges: Map<Node<'a>, Set<Node<'a>>>, nodes: Set<Node<'a>>) -> Self;
    fn subgraph(&'a self, nodes: impl Iterator<Item=&'a str>) -> Self;
    fn r#do(&'a self, nodes: impl Iterator<Item=&'a str>) -> Self;
}

#[derive(Debug)]
pub struct DiGraph<'a> {
    edges: Rc<Map<Node<'a>, Set<Node<'a>>>>,
    nodes: Box<Set<&'a str>>,
    orphans: Box<Set<&'a str>>,
}

#[derive(Debug)]
pub struct BiGraph<'a> {
    edges: Rc<Map<Node<'a>, Set<Node<'a>>>>,
    nodes: Box<Set<&'a str>>,
    orphans: Box<Set<&'a str>>,
}

impl<'a> DiGraph<'a> {
    pub fn parents (&self, x: &'a str) -> Set<&'a str> {
        let empty = Set::new();
        let elems = match self.edges.get(x) {
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
            .filter(|(_, v)| **v == 0)
            .map(|(k, _)| *k)
            .collect();
    }

    pub fn count_parents(&self) -> Map<&'a str, i32> {
        let mut n_parents: Map<&str, i32> = Map::new();
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

impl<'a> Graph<'a> for DiGraph<'a> {
    fn from_elems(edges: Map<Node<'a>, Set<Node<'a>>>, nodes: Set<Node<'a>>) -> Self {
        DiGraph {
            edges: Rc::new(edges),
            nodes: Box::new(nodes),
            orphans: Box::new(Set::new())
        }
    }

    fn subgraph(&self, nodes: impl Iterator<Item=&'a str>) -> Self {
        DiGraph {
            edges: Rc::clone(&self.edges),
            nodes: Box::new(make_set(nodes)),
            orphans: self.orphans.clone()
        }
    }

    fn r#do(&self, nodes: impl Iterator<Item=&'a str>) -> Self {
        DiGraph {
            edges: Rc::clone(&self.edges),
            nodes: self.nodes.clone(),
            orphans: Box::new(set_union(&*self.orphans, &make_set(nodes))) }
    }
}

impl<'a> Graph<'a> for BiGraph<'a> {
    fn from_elems(edges: Map<Node<'a>, Set<Node<'a>>>, nodes: Set<Node<'a>>) -> Self {
        BiGraph {
            edges: Rc::new(edges),
            nodes: Box::new(nodes),
            orphans: Box::new(Set::new())
        }
    }

    fn subgraph(&self, nodes: impl Iterator<Item=&'a str>) -> Self {
        BiGraph {
            edges: self.edges.clone(),
            nodes: Box::new(make_set(nodes)),
            orphans: self.orphans.clone()
        }
    }

    fn r#do(&self, nodes: impl Iterator<Item=&'a str>) -> Self {
        BiGraph {
            edges: self.edges.clone(),
            nodes: self.nodes.clone(),
            orphans: Box::new(set_union(&*self.orphans, &make_set(nodes)))
        }
    }
}

impl<'a> BiGraph<'a> {
    fn get_component (&self, node: Node<'a>) -> Set<Node<'a>> {
        let mut acc = Set::new();
        let mut queue = Vec::from([node]);
        loop {
            match queue.pop() {
                None => break,
                Some(node) => {
                    if acc.insert(node) {
                        match self.edges.get(node) {
                            Some(siblings) => queue.extend(siblings),
                            None => {}
                        }
                    }
                }
            }
        }
        return acc;
    }

    pub fn c_components (&self) -> Vec<Set<Node<'a>>> {
        let mut unvisited: Set<Node<'a>> = self.nodes.iter().map(|e| *e).collect();
        let mut components = Vec::new();

        for node in self.nodes.iter() {
            if unvisited.contains(node) {
                let node_component = self.get_component(node);
                for sibling in node_component.iter() {
                    unvisited.remove(sibling);
                }
                components.push(node_component);
            }
        }

        return components;
    }
}