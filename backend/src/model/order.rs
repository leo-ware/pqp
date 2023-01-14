use std::{collections::HashSet, hash::Hash};

use crate::{
    utils::{
        defaults::{Map, Set},
        set_utils::{make_set, get_one}
    },
    graph::Node
};

pub struct Order {
    map: Map<Node, i32>,
    vars: Vec<Node>,
}

impl Order {
    pub fn from_vec(vec: Vec<Node>) -> Option<Order> {
        let mut map: Map<Node, i32> = Map::new();
        for (i, val) in vec.iter().enumerate() {
            match map.insert(*val, i as i32) {
                None => (),
                Some(_) => {
                    return None;
                }
            }
        }
        Some(Order {vars: vec, map})
    }

    pub fn from_map(map: Map<Node, i32>) -> Option<Order> {
        let mut vars: Vec<Node> = map.keys().cloned().collect();

        let index: HashSet<i32> = map.values().cloned().collect();
        let index_should: HashSet<i32> = (0..vars.len()).map(|e| e as i32).collect();
        if index != index_should {
            return None;
        }

        let mut vars_set = HashSet::new();

        for (node, val) in map.iter() {
            if vars_set.insert(*node) {
                vars[*val as usize] = *node;
            } else {
                return None
            }
        }
        
        Some(Order {vars, map})
    }

    pub fn val(&self, node: &Node) -> Option<&i32> {
        self.map.get(node)
    }

    pub fn order(&self) -> &Vec<Node> {
        &self.vars
    }

    pub fn lt(&self, a: &Node, b: &Node) -> Option<bool> {
        if let Some(a_val) = self.map.get(a) {
            if let Some(b_val) = self.map.get(b) {
                return Some(a_val < b_val);
            }
        }
        None
    }

    pub fn predecessors(&self, var: &Node) -> Option<Vec<Node>> {
        match self.map.get(var) {
            None => None,
            Some(val) => {
                let mut vars = Vec::new();
                for i in 0..*val {
                    vars.push(self.vars[i as usize]);
                }
                Some(vars)
            }
        }
    }

    pub fn min(&self, vars: &Set<Node>) -> Option<Node> {
        let mut min_v = get_one(vars)?;
        for node in vars.iter() {
            if let Some(lt) = self.lt(node, &min_v) {
                if lt {
                    min_v = *node;
                }
            }
        }
        return Some(min_v);
    }

    pub fn set_predecessors(&self, vars: &Set<Node>) -> Option<Vec<Node>> {
        match self.min(vars) {
            None => Some(self.vars.clone()),
            Some(min) => self.predecessors(&min)
        }
    }
}