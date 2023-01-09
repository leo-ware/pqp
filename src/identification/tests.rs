#![cfg(test)]

use super::id;
use crate::{
    model::{
        Model,
        examples::frontdoor_model
    },
    utils::defaults::{set, Set}, form::Form,
};

#[test]
fn test_backdoor() {
    let model = Model::from_elems(
        vec![
            (2, vec![0, 1]),
            (1, vec![0]),
        ],
        vec![]
    );
    let estimand = id(&model, &set![2], &set![1]);
    let answer = Form::marginal(set![0], Form::product(vec![
        Form::prob(vec![0]),
        Form::cond_prob(vec![2], vec![0, 1]),
    ])).cond_expand().simplify();

    assert_eq!(estimand, answer);
}

// #[test]
// fn test_frontdoor() {
//     let model = frontdoor_model();
//     let estimand = id(&model, &set![2], &set![1]);
//     let answer = Form::marginal(set![1],
//         Form::product(vec![
//             Form::cond_prob(vec![1], vec![0]),
//             Form::marginal(set![0],
//                 Form::product(vec![
//                     Form::prob(vec![0]),
//                     Form::cond_prob(vec![2], vec![0, 1]),
//                 ])
//             )
//         ])
//     ).cond_expand().simplify();

//     assert_eq!(estimand, answer);

// }