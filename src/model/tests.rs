#![cfg(test)]

use crate::{
    model::{Model, ModelBuilder},
    graph::Graph,
    defaults::Set, set_utils::make_set,
};

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
    assert_eq!(make_set(abd.order().into_iter()), Set::from([a, b, d]));
    assert_eq!(abd.dag.ancestors(d), Set::new());
    assert_eq!(abd.dag.ancestors(a), Set::from([b, d]));
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
    let order = model.order();
    assert_eq!(order[3], d);
    assert_eq!(order[0], a);
}