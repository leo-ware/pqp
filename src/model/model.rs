use std::collections::{HashMap, HashSet};
use std::iter::FromIterator;
use unordered_pair::UnorderedPair;
use cute::c;

use crate::form::Form;

#[derive(Debug, PartialEq, Eq)]
#[allow(dead_code)]
pub struct Model<'a> {
    dag: HashMap<&'a str, HashSet<&'a str>>,
    confounded: HashSet<UnorderedPair<&'a str>>,
    vars: HashSet<&'a str>,
}

#[allow(dead_code, unused_mut)]
impl<'a> Model<'a> {
    pub fn new (dag: &[(&'a str, &[&'a str])], confounded: &[(&'a str, &'a str)]) -> Model<'a> {
        let mut dag_map = HashMap::new();
        let mut confounded_set = HashSet::new();
        let mut vars_set = HashSet::new();

        for (x, p_x) in dag.iter() {
            let mut parents = HashSet::new();
            for parent in p_x.iter() {
                parents.insert(*parent);
                vars_set.insert(*parent);
            }
            vars_set.insert(*x);
            dag_map.insert(*x, parents);
        }

        for (x, y) in confounded.iter() {
            vars_set.extend(&[*x, *y]);
            confounded_set.insert(UnorderedPair(*x, *y));
        }

        return Model {dag: dag_map, confounded: confounded_set, vars: vars_set};
    }

    pub fn ancestors_block (&self, x: HashSet<&'a str>, block: HashSet<&str>) -> HashSet<&'a str> {

        let mut a = HashSet::new();
        let mut acc = Vec::new();

        for var in x {
            if !block.contains(var) {
                acc.push(var);
            }
        }
        
        loop {
            match acc.pop() {
                None => break,
                Some(next) => {
                    match self.dag.get(next) {
                        None => continue,
                        Some(parents) => {
                            for parent in parents.iter() {
                                if !a.contains(parent) {
                                    a.insert(*parent);
                                    if !block.contains(*parent) {
                                        acc.push(*parent);
                                    }
                                }
                            }
                        }
                    }
                },
            }
        }

        return a;
    }

    pub fn ancestors (&self, x: HashSet<&'a str>) -> HashSet<&'a str> {
        return self.ancestors_block(x, HashSet::new());
    }

    pub fn c_components (&self) -> Vec<HashSet<&str>> {
        let mut components: Vec<HashSet<& str>> = Vec::new();
        for pair in self.confounded.iter() {
            let mut inserted = false;

            for component in components.iter_mut() {
                if component.contains(pair.0) || component.contains(pair.1) {
                    component.extend([pair.0, pair.1]);
                    inserted = true;
                    break;
                }
            }

            if !inserted {
                let mut new_component = HashSet::new();
                new_component.extend([pair.0, pair.1]);
                components.push(new_component);
            }
        }
        
        return components;
    }

    pub fn topological_sort (&self) -> Vec<&str> {
        let mut n_kids = HashMap::new();
        for var in self.vars.iter() {
            n_kids.insert(*var, 0);
        }

        for (_, parents) in self.dag.iter() {
            for parent in parents {
                *n_kids.entry(*parent).or_insert(0) += 1;
            }
        }

        let mut queue = Vec::new();
        for (var, count) in n_kids.iter() {
            if *count == 0 {
                queue.push(*var);
            }
        }

        let mut order = Vec::new();
        loop {
            match queue.pop() {
                None => break,
                Some(x) => {
                    order.push(x);
                    if self.dag.contains_key(x) {
                        for parent in self.dag[x].iter() {
                            *n_kids.entry(*parent).or_insert(0) -= 1;
                            if *n_kids.entry(*parent).or_insert(0) == 0 {
                                queue.push(*parent);
                            }
                        }
                    }
                }
            }
        }

        return order;
    }

    pub fn subgraph (&'a self, vars: HashSet<&'a str>) -> Model {
        let mut dag = self.dag.clone();
        let mut confounded = self.confounded.clone();

        for (key, _) in self.dag.iter() {
            if !vars.contains(*key) {
                dag.remove(*key);
            } else {
                dag.entry(*key).and_modify(|e| {
                    e.retain(|v| {
                        return vars.contains(*v);
                    });
                });
            }
        }

        for pair in self.confounded.iter() {
            if !(vars.contains(pair.0) && vars.contains(pair.1)) {
                confounded.remove(pair);
            }
        }

        return Model {dag, confounded, vars};
    }

    pub fn id (&self, y: HashSet<&str>, x: HashSet<&str>) -> Form {
        // step 1
        if x.is_empty() {
            return Form::Sum(
                HashSet::from_iter(self.vars.difference(&y).map(|e| *e)),
                Box::new(Form::P(c![*x, for x in y.iter()], None)),
            );
        }

        // step 2
        let a_y = self.ancestors(y);
        for var in self.vars.iter() {
            if !a_y.contains(*var) {
                return self.subgraph(a_y).id(y, HashSet::from_iter(x.union(&a_y).map(|e| *e)));
            }
        }

        // step 3
        let a_y_c = self.ancestors_block(y, x);
        let mut w = self.vars.clone();
        w.retain(|e| !a_y_c.contains(*e) && !x.contains(*e));
        if !w.is_empty() {
            return self.id(y, HashSet::from_iter(x.union(&w).map(|e| *e)));
        }

        // step 4
        let c_components = self.c_components();
        if c_components.len() > 1 {
            return Form::Sum(
                HashSet::from_iter(iter),
                ()
            );
        }

        return None;
    }

}
