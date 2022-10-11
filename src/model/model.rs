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
    pub fn new() -> ModelBuilder {
        ModelBuilder { dag: GraphBuilder::new(), confounded: GraphBuilder::new() }
    }

    pub fn from_elems(dag: Vec<(Node, Vec<Node>)>, confounded: Vec<(Node, Node)>) -> ModelBuilder {
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
    pub fn from_elems (dag: Vec<(Node, Vec<Node>)>, confounded: Vec<(Node, Node)>) -> Model {
        ModelBuilder::to_model(Box::new(ModelBuilder::from_elems(dag, confounded)))
    }

    pub fn from_graphs (dag: DiGraph, confounded: BiGraph) -> Model {
        let vars = union(&dag.get_nodes(), &confounded.get_nodes());
        Model {dag, confounded, vars}
    }

    pub fn order(&self) -> Vec<Node> {
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
}