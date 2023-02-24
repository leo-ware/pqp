use serde_json::Value;
use std::{
    result::Result,
    error::Error,
    fmt::Display, num::ParseIntError
};
use crate::{
    graph::{Node, ConcreteGraph},
    utils::defaults::{Set, Map},
};

pub trait Serializable: Sized {
    fn to_serde(&self) -> Value;
    fn from_serde(v: Value) -> Result<Self, String>;
}

pub fn recover_graph(json: Value) -> Result<(Map<Node, Set<Node>>, Set<Node>), String> {
    let edges_raw = if let Some(edges_recov) = json.get("edges"){
        if let Some(edges) = edges_recov.as_object() {
            edges
        } else {
            return Err("Edges is not an object".to_string());
        }
    } else {
        return Err("edges attribute not found".to_string());
    };

    let mut edges = edges_raw.iter().map(|(from, to)| {
        let from: Result<Node, ParseIntError> = from.parse();
        let to = to
            .as_array()
            .iter()
            .map(|to| to.as_str()?.parse().ok())
            .collect::<Option<Set<Node>>>()?;
        Some((from, to))
    }).collect::<Option<Map<Node, Set<Node>>>>();

    let nodes = if let Some(nodes_recov) = json.get("nodes"){
        if let Some(nodes) = nodes_recov.as_array() {
            nodes
        } else {
            return Err("Nodes is not an array".to_string());
        }
    } else {
        return Err("nodes attribute not found".to_string());
    };

    let nodes = nodes.iter().map(|node| node.as_str()?.parse().ok()).collect::<Option<Set<Node>>>()?;
    Ok((edges, nodes))
}

pub fn write_graph<T: ConcreteGraph>(g: &T) -> Value {
    let mut edges = serde_json::Map::new();
    for (from, to) in g.get_edges().iter() {
        edges.insert(from.to_string(), serde_json::Value::Array(
            to.iter().map(Node::to_serde).collect()
        ));
    }
    let nodes = serde_json::Value::Array(
        g.get_nodes().iter().map(Node::to_serde).collect()
    );
    serde_json::Value::Object(serde_json::Map::from_iter(vec![
        ("edges".to_string(), serde_json::Value::Object(edges)),
        ("nodes".to_string(), nodes)
    ]))
}