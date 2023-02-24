use std::num::ParseIntError;
use rand::{thread_rng, Rng};
use crate::model::serialize::Serializable;

pub type Node = i32;

pub fn make_nodes(n: i32) -> Vec<Node> {
    let mut nodes: Vec<Node> = Vec::new();
    let mut rng = rand::thread_rng();
    for _ in 0..n {
        nodes.push(rng.gen());
    }
    nodes
}

impl Serializable for Node {
    fn to_serde(&self) -> serde_json::Value {
        serde_json::Value::Number(serde_json::Number::from(*self))
    }

    fn from_serde(v: serde_json::Value) -> Result<Self, String> {
        let res = v.to_string().parse();
        match res {
            Ok(x) => Ok(x),
            Err(e) => {
                Err(format!("error parsing Node, {:?}", e.kind()))
            }
        }
    }
}