#![cfg(test)]
use std::collections::HashSet;

use super::model;

#[test]
fn test() {
    let foo = model::Model::new(
        &[
            ("x", &["z", "w"]),
            ("y", &["x", "z"]),
        ],
        &[
            ("z", "w"),
            ("y", "z"),
        ]
    );

    assert_eq!(foo.ancestors("x"), HashSet::from(["z", "w"]));
    assert_eq!(foo.ancestors("y"), HashSet::from(["x", "z", "w"]));
    assert_eq!(foo.ancestors("z"), HashSet::from([]));

    assert_eq!(foo.ancestors_block("y", Vec::from(["x"])), HashSet::from(["x", "z"]));
    assert_eq!(foo.ancestors_block("x", Vec::from(["x"])), HashSet::from([]));

    assert_eq!(foo.c_components(), Vec::from([HashSet::from(["y", "z", "w"])]));
    assert!(
        foo.topological_sort() == Vec::from(["y", "x", "z", "w"]) ||
        foo.topological_sort() == Vec::from(["y", "x", "w", "z"])
    );
}