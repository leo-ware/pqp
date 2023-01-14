use rand::{thread_rng, Rng};

pub type Node = i32;

pub fn make_nodes(n: i32) -> Vec<Node> {
    let mut nodes: Vec<Node> = Vec::new();
    let mut rng = rand::thread_rng();
    for _ in 0..n {
        nodes.push(rng.gen());
    }
    nodes
}