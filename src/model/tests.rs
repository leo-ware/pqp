#![cfg(test)]

use crate::{
    model::{Model, ModelBuilder},
    graph::{
        Graph,
        make_nodes,
    },
    utils::{
        defaults::{Set, Map},
        set_utils::make_set,
    },
    set, P
};

use super::{order::Order, examples::frontdoor_model};

#[test]
fn subgraphing() {
    let (a, b, c, d) = (1, 2, 3, 4);
    let model = Model::from_elems(
        vec![
            (a, vec![b, c, d]),
            (b, vec![c, d]),
            (c, vec![d])
        ],
        vec![(a, d)]
    );

    let abd = model.subgraph(&Set::from([a, b, d]));
    assert_eq!(make_set(abd.order_vec().into_iter()), Set::from([a, b, d]));
    assert_eq!(abd.dag.ancestors(d), Set::new());
    assert_eq!(abd.dag.ancestors(a), Set::from([b, d]));
}

#[test]
fn c_components_subgraph () {
    let model = frontdoor_model();

    fn vec_and_sort(cs: Vec<Set<i32>>) -> Vec<Vec<i32>> {
        let mut new = vec![];
        for c in cs {
            let mut c_vec: Vec<i32> = c.into_iter().collect();
            c_vec.sort();
            new.push(c_vec);
        }
        new.sort();
        return new;
    }

    let c_components = model.confounded.c_components();
    assert_eq!(vec_and_sort(c_components), vec![
        vec![0, 2],
        vec![1],
    ]);

    let graph_sub_c_components = model.confounded.subgraph(&set![1, 2]).c_components();
    assert_eq!(vec_and_sort(graph_sub_c_components), vec![
        vec![1],
        vec![2],
    ], "test 1");

    let sub_c_components = model.subgraph(&set![1, 2]).confounded.c_components();
    assert_eq!(vec_and_sort(sub_c_components), vec![
        vec![1],
        vec![2],
    ]);


}

#[test]
fn order() {
    let (a, b, c, d) = (1, 2, 3, 4);
    let model = Model::from_elems(
        vec![
            (a, vec![b, c]),
            (c, vec![d]),
        ],
        vec![]
    );
    let order = model.order_vec();
    assert_eq!(order[3], d);
    assert_eq!(order[0], a);
}

#[test]
fn test_nodes_added_graphs() {
    let model = Model::from_elems(
        vec![
            (2, vec![0, 1]),
            (1, vec![0]),
        ],
        vec![(1, 4)],
    );

    assert_eq!(model.get_nodes(), model.get_dag().get_nodes());
    assert_eq!(model.get_nodes(), model.get_confounded().get_nodes());
}

#[test]
fn test_order_from_vec () {
    assert!(!Order::from_vec(Vec::new()).is_none());
    assert!(!Order::from_vec(Vec::from([1])).is_none());
    assert!(!Order::from_vec(make_nodes(10)).is_none());
    assert!(Order::from_vec(Vec::from([1, 2, 1])).is_none());
}

#[test]
fn test_order_from_map () {
    assert!(!Order::from_map(Map::from([(0, 0), (1, 1), (2, 2)])).is_none());
    assert!(Order::from_map(Map::from([(0, 0), (0, 1), (2, 2)])).is_none());
    assert!(Order::from_map(Map::from([(0, 0), (1, 2), (2, 2)])).is_none());
}

#[test]
fn test_order_utils () {
    let vec = make_nodes(10);
    let order = Order::from_vec(vec.clone()).expect("failure intializing Order");

    assert!(order.lt(&vec[4], &vec[5]).expect("lt failed to return"));
    assert!(order.lt(&vec[0], &vec[2]).expect("lt failed to return"));
    assert_eq!(order.predecessors(&vec[5]).expect("failed to get predecessors").len(), 5);
    assert_eq!(order.val(&vec[5]), Some(&5));
    assert_eq!(order.val(&vec[9]), Some(&9));
    assert_eq!(order.val(&10), None)
}

#[test]
fn test_order_predecessors_set() {
    let order_vec = make_nodes(10);
    let order = Order::from_vec(order_vec.clone()).expect("failure intializing Order");

    let s1 = set![order_vec[4], order_vec[6], order_vec[8]];
    let a1 = vec![order_vec[0], order_vec[1], order_vec[2], order_vec[3]];
    assert_eq!(order.set_predecessors(&s1), Some(a1));

    assert_eq!(order.set_predecessors(&set![order_vec[0]]), Some(vec![]),
        "set_predecessors should return empty vec when none exist");

    assert_eq!(order.set_predecessors(&set![]), Some(order_vec.clone()),
        "set_predecessors should return full order on empty query");

    assert_eq!(order.set_predecessors(&set![15]), None,
        "set_predecessors should return None when no queries in order");
    
    // assert_eq!(order.set_predecessors(&set![15, order_vec[1]]), Some(vec![order_vec[0]]),
    //     "set_predecessors should return when at least one query is good");
}