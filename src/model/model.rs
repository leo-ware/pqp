use std::collections::{HashMap as Map, HashSet as Set};
use cute::c;

use crate::form::Form;
use crate::utils::{set_difference, set_union};
use crate::graph::graph::{GraphBuilder, DiGraph};

#[derive(Debug)]
pub struct Model<'a> {
    dag: GraphBuilder<'a>,
    confounded: GraphBuilder<'a>,
    vars: Set<&'a str>
}

#[derive(Debug)]
struct SubgraphModel<'a> {
    dag: DiGraph<'a>,
    confounded: DiGraph<'a>,
    vars: &'a Set<&'a str>,
}

impl<'a> Model<'a> {
    fn from(dag: impl Iterator<Item=(&'a str, impl Iterator<Item=&'a str>)>, confounded: impl Iterator<Item=(&'a str, &'a str)>) -> Model<'a> {

        // build dag
        let mut dag_graph = GraphBuilder::new();
        let mut vars = Set::new();
        for (k, v) in dag {
            vars.insert(k);
            for x in v {
                vars.insert(x);
                dag_graph.insert(k, x);
            }
        }
        let confounded_vec = c![x, for x in confounded];
        for (a, b) in confounded_vec.iter() {
            vars.extend([*a, *b]);
        }
        let dag_view = dag_graph.view();

        // work out order
        let dag_order = dag_view.order();
        let vars_copy: Set<&'a str> = vars.iter().map(|e| *e).collect();
        for x in dag_order.iter() {
            vars.remove(*x);
        }
        let mut order: Vec<&str> = vars.iter().map(|e| *e).collect();
        order.extend(dag_order);
        let order_values: Map<&str, i32> = order.iter().enumerate().map(|(a, b)| (*b, a as i32)).collect();

        // build confounded graph
        let mut confounded_graph = GraphBuilder::new();
        for (a, b) in confounded_vec {
            vars.extend([a, b]);
            if order_values[a] > order_values[b] {
                confounded_graph.insert(b, a);
            } else {
                confounded_graph.insert(a, b);
            }
        }

        return Model {dag: dag_graph, confounded: confounded_graph, vars: vars_copy};
    }

    fn subgraph_model(&'a self, nodes: &'a Set<&'a str>, intervene: &'a Set<&'a str>) -> SubgraphModel {
        SubgraphModel::<'a> {
            dag: self.dag.subgraph(nodes, intervene),
            confounded: self.confounded.subgraph(nodes, intervene),
            vars: nodes,
        }
    }

}

impl<'a> SubgraphModel<'a> {

    fn subgraph_model(&'a self, nodes: &'a Set<&'a str>, intervene: &'a Set<&'a str>) -> SubgraphModel {
        SubgraphModel::<'a> {
            dag: self.dag.subgraph(nodes, intervene),
            confounded: self.confounded.subgraph(nodes, intervene),
            vars: nodes,
        }
    }

    fn intervene(&'a self, intervene: &'a Set<&'a str>) -> SubgraphModel {
        SubgraphModel::<'a> {
            dag: self.dag.intervene(intervene),
            confounded: self.confounded.intervene(intervene),
            vars: self.vars,
        }
    }

    fn c_components(&self) -> Vec<Set<&'a str>> {
        return c![self.confounded.ancestors(root), for root in self.confounded.root_set()];
    }

    fn id<'b>(&self, outcome: &'b Set<&'a str>, treatment: &'b Set<&'a str>) -> Form<'b> {
        // step 1
        if treatment.len() == 0 {
            return Form::Marginal(
                set_difference(self.vars, outcome),
                Box::new(Form::P(c![*v, for v in self.vars], None))
            );
        }

        // step 2
        let an_y = self.dag.ancestors_set(&outcome);
        if *self.vars != an_y {
            return Form::Marginal(
                set_difference(self.vars, &outcome),
                Box::new(self.id(treatment, &set_union(&treatment, &an_y)))
            );
        }

        // step 3
        let a_y_intervene = self.dag.intervene(treatment).ancestors_set(outcome);
        let w = set_union(&set_union(self.vars, treatment), &a_y_intervene);
        if w.len() != 1 {
            return self.id(outcome, &set_union(&treatment, &w));
        }

        // step 4
        let c_components_intervene = self
            .subgraph_model(&set_difference(&self.vars, &treatment), &Set::new())
            .c_components();
        if c_components_intervene.len() > 1 {
            return Form::Marginal(
                set_difference(self.vars, &set_union(&treatment, &outcome)),
                Box::new(Form::Product(c![self.id(&s, &set_difference(self.vars, &s)), for s in c_components_intervene]))
            )
        }

        // step 5
        let c_components = self.c_components();
        if c_components.len() == 1 {
            return Form::Fail;
        }

        let s = match c_components.pop() {
            Some(v) => v,
            None => panic!("argggg!!"),
        };
        for comp in c_components_intervene {
            if s.is_subset(&comp) {
                // step 6
                if s.len() == comp.len() {
                    return Form::Marginal(
                        set_difference(&s, &self.vars),
                        Box::new(Form::P(c![i, for i in s], None)),
                    )
                // step 7
                } else {
                    
                }
            }
        }

        return ();
        panic!("id assumptions violated");
        
    }
}