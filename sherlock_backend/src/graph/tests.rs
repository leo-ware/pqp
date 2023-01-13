#![cfg(test)]

use crate::{model::{self, examples::frontdoor_model}, utils::set_utils::make_set, set};
use super::{GraphBuilder, Set, DiGraph, BiGraph, Graph, node::{Node, make_nodes}};

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

    assert_eq!(make_set(dg.root_set().into_iter()), set![a, c], "root set");
    assert_eq!(dg.ancestors(a), Set::from([b]), "ancestors a");
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
    assert_eq!(graph.ancestors(a), Set::from([b, c, d]), "ancestors a");
    assert_eq!(graph.ancestors(b), Set::from([d]), "ancestors b");
    assert_eq!(graph.ancestors(c), Set::from([d]), "ancestors d");
    assert_eq!(graph.ancestors(d), Set::from([]), "ancestors c");

    let abd = graph.subgraph(&Set::from([a, b, d]));
    assert_eq!(abd.ancestors(a), Set::from([b, d]), "subg ancestors a");
    assert_eq!(abd.ancestors(b), Set::from([d]), "subg ancestors b");
    
    let intv = graph.r#do(&Set::from([b, c]));
    assert_eq!(intv.ancestors(a), Set::from([b, c]), "intv ancestors a");
    assert_eq!(intv.ancestors(b), Set::new(), "intv ancestors b");
}

#[test]
fn test_ancestors_set () {
    /*
    causal diagram

    1 <--- 2 <------ 4 <--
        |        |        |
         -- 3 <--         |
        |                 |
    5 <------------------ 6

    */
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
        graph.r#do(&set![4]).ancestors_set(&Set::from([1])),
        Set::from([2, 3, 4])
    );
    assert_eq!(
        graph.r#do(&set![4]).ancestors_set(&set![1, 5]),
        Set::from([2, 3, 4, 6])
    );

}

#[test]
fn test_ancestors_backdoor() {
    let graph = DiGraph::from_edges(vec![
        (1, 0),
        (2, 1),
        (2, 0),
    ]);
    assert_eq!(graph.ancestors(2), set!(0, 1));

    let a_y_intervene_x = graph.r#do(&set![1]).ancestors(2);
    assert_eq!(a_y_intervene_x, set![0, 1]);
}

#[test]
fn test_ancestors_frontdoor() {
    let fd = frontdoor_model();
    assert_eq!(fd.ancestors_set_inc(&set!(2, 0)), set!(2, 1, 0));
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

#[test]
fn test_c_components_backdoor() {
    let model = model::examples::backdoor_model();

    let c_components = model.confounded.c_components();
    assert_eq!(c_components.len(), 3);
    for component in c_components.iter() {
        assert_eq!(component.len(), 1);
    }
    
    let subgraph_c_components =  model.subgraph(&set![0, 2]).confounded.c_components();
    assert_eq!(subgraph_c_components.len(), 2);
    assert_ne!(subgraph_c_components[0], subgraph_c_components[1]);
}

#[test]
fn test_random_nodes_len () {
    let n0 = make_nodes(0);
    let n1 = make_nodes(1);
    let n15 = make_nodes(15);

    assert_eq!(n0.len(), 0);
    assert_eq!(n1.len(), 1);
    assert_eq!(n15.len(), 15);
}