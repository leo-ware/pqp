use rand::{thread_rng, Rng};

pub type Node = i32;

/// Generates a vector of n nodes, implemented as random 32 bit integers.
/// Suggested usage: `let [a, b, c] = make_nodes(3)[..]`
pub fn make_nodes(n: i32) -> Vec<Node> {
    let mut nodes: Vec<Node> = Vec::new();
    let mut rng = rand::thread_rng();
    for _ in 0..n {
        nodes.push(rng.gen());
    }
    nodes
}