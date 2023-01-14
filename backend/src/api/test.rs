// #![cfg(test)]

// use super::wrapper::FormWrapper;
// use crate::{
//     utils::defaults::{set, Set},
// };

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