use std::{collections::{HashMap, HashSet as Set}, iter::{Filter, FromIterator}};

#[derive(Debug)]
pub struct DirectedGraph<'a> {
    nodes: Set<&'a str>,
    edges: HashMap<&'a str, Set<&'a str>>
}

impl<'a> DirectedGraph<'a> {
    fn new () -> DirectedGraph<'a> {
        return DirectedGraph {
            edges: HashMap::new(),
            nodes: Set::new(),
        };
    }

    fn insert (&self, from: &'a str, to: &'a str) {
        self.nodes.extend([from, to]);
        self.edges.entry(from).or_insert(Set::new());
        self.edges.entry(from).and_modify(|s| {s.insert(to);});
    }

    fn parents (&self, x: &'a str) -> Set<&'a str> {
        let elems = match self.edges.get(x) {
            Some(kids) => kids,
            None => &Set::new(),
        };
        let filtered = elems.into_iter()
            .filter(|elem| self.nodes.contains(**elem))
            .map(|elem| *elem);
        return Set::from_iter(filtered);
    }

    fn ancestors (&self, x: &'a str) -> Vec<&'a str> {
        let acc = Vec::new();
        let queue = Vec::new();
        queue.push(x);
        
        for _ in 0..(self.nodes.len() + 1) {
            match queue.pop() {
                Some(elem) => {
                    for parent in self.parents(elem) {
                        if self.nodes.contains(parent) {
                            queue.push(parent);
                            acc.push(parent);
                        }
                    }
                },
                None => return acc,
            }
        }

        panic!("infinite loop detected");
    }


}