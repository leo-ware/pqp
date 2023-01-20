#![cfg(test)]

use super::wrapper::{FormWrapper, ModelWrapper};
use crate::{
    utils::defaults::{set, Set},
};

#[test]
fn test_wrapper_bowgraph() {
    let mut m = ModelWrapper::new();
    m.add_effect("x", "y");
    m.add_confounding("x", "y");
    let res = m.id(set!["y".to_string()], set!["x".to_string()], set![]);
    assert_eq!(res.estimand_json, "{type: Hedge}");
}

// #[test]
// fn test_foo() {
//     let f = FormWrapper::Quotient(
//         Box::new(FormWrapper::P(vec!["C".to_string()], vec![])),
//         Box::new(FormWrapper::Product(vec![
//             FormWrapper::P(vec!["A".to_string(), "B".to_string()], vec![]),
//             FormWrapper::Marginal(
//                 set!["A".to_string()],
//                 Box::new(FormWrapper::P(vec!["B".to_string()], vec![]))
//             ),
//             ]))
//     );
// }