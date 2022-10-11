use cute::c;
use crate::form::Form;
use crate::defaults::{Set, Map};
use crate::set_utils::{union, make_set, difference, intersection};
use crate::graph::{GraphBuilder, DiGraph, BiGraph, Graph, Node};

pub struct ModelBuilder {
    dag: GraphBuilder,
    confounded: GraphBuilder,
}

impl<'a> ModelBuilder {
    fn new() -> ModelBuilder {
        ModelBuilder { dag: GraphBuilder::new(), confounded: GraphBuilder::new() }
    }

    pub fn from(dag: Vec<(Node, Vec<Node>)>, confounded: Vec<(Node, Node)>) -> ModelBuilder {
        let mut builder = ModelBuilder::new();
        for (from, to) in dag {
            for target in to {
                builder.dag.add_edge(from, target);
            }
        }

        for (a, b) in confounded {
            builder.confounded.add_edge(a, b);
        }

        return builder;
    }

    pub fn to_model (builder: Box<ModelBuilder>) -> Model {
        let vars = union(&builder.dag.get_nodes(), &builder.confounded.get_nodes());
        Model {
            dag: GraphBuilder::to_digraph(builder.dag),
            confounded: GraphBuilder::to_bigraph(builder.confounded),
            vars
        }
    }
}


#[derive(Debug)]
pub struct Model {
    pub dag: DiGraph,
    pub confounded: BiGraph,
    vars: Set<Node>
}

impl Graph for Model {
    fn subgraph(&self, nodes: &Set<Node>) -> Self {
        Model {
            dag: self.dag.subgraph(nodes),
            confounded: self.confounded.subgraph(nodes),
            vars: nodes.clone()
        }
    }

    fn r#do(&self, nodes: &Set<Node>) -> Self {
        Model {
            dag: self.dag.r#do(nodes),
            confounded: self.confounded.r#do(nodes),
            vars: self.vars.clone()
        }
    }

    fn get_nodes(&self) -> &Set<Node> {
        &self.vars
    }
}

impl Model {
    fn order(&self) -> Vec<Node> {
        let res_set = difference(
            self.confounded.get_nodes(), 
            self.dag.get_nodes()
        );
        let mut res = Vec::new();
        for r in res_set {
            res.push(r);
        }
        res.extend(self.dag.order());
        return res;
    }

    fn _id(&self, y: &Set<Node>, x: &Set<Node>, p: Form) -> Form {
        let v = &self.vars;
        
        // step 1
        if x.len() == 0 {
            return Form::marginal(difference(v, &y), p);
        }

        // step 2
        let ancestors_y = self.dag.ancestors_set(&y);
        if self.vars != ancestors_y {
            let subg = self.subgraph(&ancestors_y);
            return subg
                ._id(
                    y,
                    &intersection(x, &ancestors_y),
                    Form::marginal(difference(v, &ancestors_y), p)
                );
        }

        // step 3
        let a_y_intervene = self.dag
            .r#do(x)
            .ancestors_set(y);
        let w = difference(&difference(v, x), &a_y_intervene);
        if !w.is_empty() {
            return self._id(y, &union(&x, &w), p);
        }

        // step 4
        let c_components_less_x = self
            .subgraph(&difference(&self.vars, &x))
            .confounded
            .c_components();
        
        if c_components_less_x.len() > 1 {
            return Form::marginal(
                difference(v, &union(&y, &x)),
                Form::product(c![
                    self._id(&s_i, &difference(v, &s_i), p.clone()),
                    for s_i in c_components_less_x
                ])
            );
        }

        // step 5
        let mut c_components = self.confounded.c_components();
        if c_components.len() == 1 {
            return Form::Fail;
        }

        // homestretch woot
        let s = c_components.pop().expect("arggg");
        for s_prime in c_components_less_x {
            if s.is_subset(&s_prime) {
                // step 6
                if s.len() == s_prime.len() {
                    return Form::marginal(
                        difference(&s, y),
                        Form::factorize(self.order(), p)
                    );
                // step 7
                } else {
                    let w = &union(&x, &s_prime);
                    return self.subgraph(&s_prime)
                        ._id(y, &intersection(&x, &s_prime), Form::factorize(self.order(), p))
                }
            }
        }

        panic!("id assumptions violated");
        
    }
}