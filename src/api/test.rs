#![cfg(test)]

use super::{
    wrapper::{FormWrapper, ModelWrapper},
    functions::id,
};
use crate::{
    utils::defaults::{set, Set},
};

#[test]
fn test_wrapper_bowgraph() {
    let mut m = ModelWrapper::new();
    m.add_effect("x", "y");
    m.add_confounding("x", "y");
    let res = m.id(set!["y".to_string()], set!["x".to_string()], set![]);
    assert_eq!(res.estimand_json, FormWrapper::Hedge.to_json());
}

#[test]
fn test_wrapper_fd() {
    let mut m = ModelWrapper::new();
    m.add_effect("x", "z");
    m.add_effect("z", "y");
    m.add_confounding("x", "y");
    let res = m.id(set!["y".to_string()], set!["x".to_string()], set![]);
    assert_ne!(res.estimand_json, FormWrapper::Hedge.to_json());
}

#[test]
fn test_wrapped_bd () {
    let mut m = ModelWrapper::new();
    m.add_effect("x", "y");
    m.add_effect("z", "y");
    m.add_effect("z", "x");

    let res = m.id(set!["y".to_string()], set!["x".to_string()], set!["z".to_string()]);
    assert_ne!(res.estimand_json, FormWrapper::Hedge.to_json());
}

#[test]
fn test_fn_id_fd () {
    let res = id(
        vec![("x".to_string(), "z".to_string()), ("z".to_string(), "y".to_string())],
        vec![("x".to_string(), "y".to_string())],
        vec!["y".to_string()],
        vec!["x".to_string()],
        vec![],
    );
    assert_ne!(res.estimand_json, FormWrapper::Hedge.to_json());
}