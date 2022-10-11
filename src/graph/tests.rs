#![cfg(test)]

use crate::{graph::Graph, set_utils::make_set};

use super::{GraphBuilder, Set, DiGraph, BiGraph};

#[test]
fn test_graph_builder () {
    let mut gb = GraphBuilder::new();
    let (a, b, c, d) = (1, 2, 3, 4);

    gb.add_edge(a, b);
    assert!(gb.get_nodes().contains(&a));
    assert!(!gb.get_nodes().contains(&c));

    gb.add_node(c);
    assert!(gb.get_nodes().contains(&c));
    assert!(!gb.get_nodes().contains(&d));
    assert!(gb.get_edges().contains_key(&a));
    assert!(gb.get_edges()[&a] == Set::from([b]));
}

#[test]
fn test_to_digraph () {
    let mut gb = GraphBuilder::new();
    let (a, b, c) = (1, 2, 3);

    gb.add_edge(a, b);
    gb.add_node(c);
    let dg = GraphBuilder::to_digraph(gb);

    assert!(dg.root_set() == vec![a, c] || dg.root_set() == vec![c, a]);
    assert_eq!(dg.ancestors(a), Set::from([b]));
    assert_eq!(dg.order().last(), Some(&b));
    assert_eq!(dg.order().len(), 3);
    assert_eq!(dg.count_parents()[&b], 1);
    assert_eq!(dg.count_parents()[&a], 0);
    assert_eq!(dg.count_parents()[&c], 0);
}

#[test]
fn test_ancestors () {
    let (a, b, c, d) = (1, 2, 3, 4);
    let graph = DiGraph::from_edges(vec![
        (a, b),
        (a, c),
        (b, d),
        (c, d),
    ]);
    assert_eq!(graph.ancestors(a), Set::from([b, c, d]));
    assert_eq!(graph.ancestors(b), Set::from([d]));
    assert_eq!(graph.ancestors(c), Set::from([d]));
    assert_eq!(graph.ancestors(d), Set::from([]));

    let abd = graph.subgraph(&Set::from([a, b, d]));
    assert_eq!(abd.ancestors(a), Set::from([b, d]));
    assert_eq!(abd.ancestors(b), Set::from([d]));
    
    let intv = graph.r#do(&Set::from([b, c]));
    assert_eq!(intv.ancestors(a), Set::from([]));
    assert_eq!(intv.ancestors(b), Set::from([d]));
}

#[test]
fn test_ancestors_set () {
    let graph = DiGraph::from_edges(vec![
        (1, 2),
        (1, 3),
        (2, 4),
        (3, 4),
        (5, 3),
        (4, 6),
        (5, 6),
    ]);
    assert_eq!(graph.ancestors_set(&Set::from([])), Set::from([]));
    assert_eq!(graph.ancestors_set(&Set::from([2, 5])), Set::from([3, 4, 6]));
    assert_eq!(
        graph.r#do(&Set::from([4])).ancestors_set(&Set::from([1])),
        Set::from([2, 3])
    );
    assert_eq!(
        graph.r#do(&Set::from([4])).ancestors_set(&Set::from([1, 5])),
        Set::from([2, 3, 6])
    );

}

#[test]
fn test_root_set () {
    let (a, b, c, d) = (1, 2, 3, 4);

    let graph = DiGraph::from_edges(vec![
        (a, b),
        (a, c),
        (b, d),
        (c, d),
    ]);
    assert_eq!(graph.root_set(), Vec::from([a]));

    let graph = DiGraph::from_edges(vec![
        (a, c),
        (b, c),
        (c, d),
    ]);
    assert_eq!(make_set(graph.root_set().into_iter()), Set::from([a, b]));
}

#[test]
fn test_to_bigraph () {
    let mut gb = GraphBuilder::new();
    let (a, b, c) = (1, 2, 3);

    gb.add_edge(a, b);
    gb.add_node(c);
    let bg = GraphBuilder::to_bigraph(gb);

    assert!(bg.c_components() == vec![Set::from([a, b]), Set::from([c])] ||
            bg.c_components() == vec![Set::from([c]), Set::from([a, b])],
            "Failed because: bg.c_components() == {:#?}", bg.c_components())
}

#[test]
fn test_c_components () {

    fn component_products(components: Vec<Set<i32>>) -> Set<i32> {
        let mut acc = Set::new();
        for c in components {
            let mut val = 1;
            for el in c {
                val = val * el;
            }
            acc.insert(val);
        }
        return acc;
    }

    let (a, b, c, d, e, f) = (2, 3, 5, 7, 11, 13);
    let graph = BiGraph::from_edges_nodes(vec![
        (a, b),
        (b, c),
        (c, d),
        (e, c),
    ], vec![f]);
    let cs = component_products(graph.c_components());
    assert_eq!(cs.len(), 2);
    assert!(cs.contains(&f));

    let graph = BiGraph::from_edges_nodes(vec![
        (a, b),
        (b, c),
        (c, b),
        (e, f),
    ], vec![d]);
    let cs = component_products(graph.c_components());
    assert_eq!(cs, Set::from([30, 143, 7]));

    let graph = BiGraph::from_edges_nodes(vec![], vec![a, b, c, d, e, f]);
    let cs = component_products(graph.c_components());
    assert_eq!(cs, Set::from([a, b, c, d, e, f]));

}