use super::Model;
use crate::graph::Graph;

pub fn backdoor_model() -> Model {
    Model::from_elems(
        vec![
            (2, vec![0, 1]),
            (1, vec![1])
        ],
        vec![]
    )
}

pub fn frontdoor_model() -> Model {
    Model::from_elems(
        vec![
            (2, vec![1]),
            (1, vec![0])
        ],
        vec![(2, 0)]
    )
}