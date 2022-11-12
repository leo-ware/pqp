#![cfg(test)]
use super::Form;
use crate::utils::defaults::{set, Set};

// #[test]
// fn test_factorize() {
//     let p = Form::prob(vec![0, 1, 2]);
//     let factorized = Form::factorize(vec![0, 1, 2], p);
//     assert_eq!(
//         factorized,
//         Form::product(vec![
//             Form::cond_prob(vec![0], vec![1, 2]),
//             Form::cond_prob(vec![1], vec![2]),
//             Form::prob(vec![2])
//         ])
//     );
// }

// #[test]
// fn test_simplify() {
//     let f = {
//         Form::product(vec![
//             Form::product(vec![
//                 Form::prob(vec![0, 3])
//             ]),
//             Form::quotient(
//                 Form::prob(vec![4]),
//                 Form::prob(vec![6, 7]),
//             ),
//         ])
//     };

//     let simple = {
//         Form::quotient(Form::product(vec![Form::prob(vec![0, 3])]), denom)
//     };

//     assert_eq!(f.simplify(), Form::marginal(set![], Form))
// }

