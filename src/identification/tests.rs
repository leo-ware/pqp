#![cfg(test)]

use super::id;
use crate::{
    model::Model,
    utils::defaults::{set, Set},
};

// #[test]
// fn backdoor() {
//     let model = Model::from_elems(
//         vec![
//             (2, vec![0, 1]),
//             (1, vec![0]),
//         ],
//         vec![]
//     );

//     // println!("{:?}", model);
//     // println!("{:?}", model.get_dag().ancestors(2));

//     let form = id(&model, &set![2], &set![1]);

//     println!("identification results: {:?}", form.simplify());
//     assert!(false);
// }