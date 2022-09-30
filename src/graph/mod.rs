mod tests;
mod graph;
mod graph_builder;

pub use graph_builder::GraphBuilder;
pub use graph::{Graph, BiGraph, DiGraph};

use std::collections::{HashMap as Map, HashSet as Set};
pub type Node<'a> = &'a str;