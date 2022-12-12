use cute::c;
use crate::form::Form;
use crate::set;
use crate::utils::defaults::{Set, Map};
use crate::utils::set_utils::{union, make_set, difference, intersection};
use crate::graph::{GraphBuilder, DiGraph, BiGraph, Graph, Node};

use super::order::Order;

pub struct ModelBuilder {
    dag: GraphBuilder,
    confounded: GraphBuilder,
}

impl<'a> ModelBuilder {
    pub fn new() -> ModelBuilder {
        ModelBuilder { dag: GraphBuilder::new(), confounded: GraphBuilder::new() }
    }

    pub fn from_elems(dag: Vec<(Node, Vec<Node>)>, confounded: Vec<(Node, Node)>) -> ModelBuilder {
        let mut builder = ModelBuilder::new();
        for (from, to) in dag {
            for target in to {
                builder.dag.add_edge(from, target);

                builder.confounded.add_node(target);
            }
            builder.confounded.add_node(from);
        }

        for (a, b) in confounded {
            builder.confounded.add_edge(a, b);
            builder.dag.add_node(a);
            builder.dag.add_node(b);
        }

        return builder;
    }

    pub fn to_model (builder: Box<ModelBuilder>) -> Model {
        let vars = union(&builder.dag.get_nodes(), &builder.confounded.get_nodes());
        Model {
            dag: GraphBuilder::to_digraph(builder.dag),
            confounded: GraphBuilder::to_bigraph(builder.confounded),
            cond_vars: set![],
            vars
        }
    }
}


#[derive(Debug)]
pub struct Model {
    pub dag: DiGraph,
    pub confounded: BiGraph,
    cond_vars: Set<Node>,
    vars: Set<Node>,
}

impl Graph for Model {
    fn subgraph(&self, nodes: &Set<Node>) -> Self {
        Model {
            dag: self.dag.subgraph(nodes),
            confounded: self.confounded.subgraph(nodes),
            vars: nodes.clone(),
            cond_vars: self.cond_vars.clone(),
        }
    }

    fn r#do(&self, nodes: &Set<Node>) -> Self {
        Model {
            dag: self.dag.r#do(nodes),
            confounded: self.confounded.r#do(nodes),
            vars: self.vars.clone(),
            cond_vars: self.cond_vars.clone(),
        }
    }

    fn get_nodes(&self) -> &Set<Node> {
        &self.vars
    }
}

impl Model {
    pub fn from_elems (dag: Vec<(Node, Vec<Node>)>, confounded: Vec<(Node, Node)>) -> Model {
        ModelBuilder::to_model(Box::new(ModelBuilder::from_elems(dag, confounded)))
    }

    pub fn from_graphs (dag: DiGraph, confounded: BiGraph) -> Model {
        let vars = union(&dag.get_nodes(), &confounded.get_nodes());
        Model {dag, confounded, vars, cond_vars: set![]}
    }

    // pub fn cond (&self, cond: &Set<Node>) -> Model {
    //     todo!();
    //     // Model {
    //     //     dag: self.dag,
    //     //     confounded: self.confounded,
    //     //     vars: self.vars,
    //     //     cond_vars: union(&self.cond_vars, &cond)
    //     // }
    // }

    // pub fn independent(&self, a: &Set<Node>, b: &Set<Node>) -> bool {
    //     todo!();

    //     // let target: Set<Node> = b.iter().cloned().filter(|node| self.vars.contains(node)).collect();
    //     // let mut confounded: Vec<Node> = a.iter().cloned().filter(|node| self.vars.contains(node)).collect();
    //     // let mut visited: Set<Node> = set!();

    //     // let add_confounded = |node| {
    //     //     if visited.insert(node) {
    //     //         confounded.push(node);
    //     //     }
    //     // };

    //     // while !confounded.is_empty() && !visited.len() == self.vars.len() {


    //     // }

    //     // return true;
    // }

    pub fn order_vec(&self) -> Vec<Node> {
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

    pub fn order(&self) -> Order {
        let order_vec = self.order_vec();
        Order::from_vec(order_vec).expect("error creating order")
    }

    pub fn get_dag(&self) -> &DiGraph {
        &self.dag
    }

    pub fn get_confounded(&self) -> &BiGraph {
        &&self.confounded
    }

    pub fn ancestors(&self, node: Node) -> Set<Node> {
        self.dag.ancestors(node)
    }

    pub fn ancestors_set(&self, s: &Set<Node>) -> Set<Node> {
        self.dag.ancestors_set(s)
    }

    pub fn ancestors_inc(&self, node: Node) -> Set<Node> {
        let mut s = self.ancestors(node);
        s.insert(node);
        return s;
    }

    pub fn ancestors_set_inc(&self, nodes: &Set<Node>) -> Set<Node> {
        let mut s = self.dag.ancestors_set(nodes);
        s = union(&s, nodes);
        return s;
    }

}