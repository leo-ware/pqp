use super::{
    form::Form,
};

use crate::utils::defaults::{set, Set};

#[test]
fn test_sort () {
    let f = Form::prob(vec![1, 2, 0]).sorted();
    let s = Form::prob(vec![0, 1, 2]);
    assert_eq!(f, Form::prob(vec![0, 1, 2]), "{:?} should equal {:?}", f, s);
}

#[test]
fn test_structural_eq () {
    let f1 = Form::product(vec![
        Form::prob(vec![0, 3]),
        Form::prob(vec![4]),
        Form::prob(vec![6, 7]),
    ]);
    let f2 = Form::product(vec![
        Form::prob(vec![6, 7]),
        Form::prob(vec![0, 3]),
        Form::prob(vec![4]),
    ]);
    assert!(f1.structural_eq(&f2));

    // more complex test involving quotients
    let f1 = Form::quotient(
        Form::product(vec![
            Form::prob(vec![0, 3]),
            Form::prob(vec![4]),
            Form::prob(vec![6, 7]),
        ]),
        Form::prob(vec![0, 1, 2]),
    );
    let f2 = Form::quotient(
        Form::product(vec![
            Form::prob(vec![6, 7]),
            Form::prob(vec![0, 3]),
            Form::prob(vec![4]),
        ]),
        Form::prob(vec![0, 1, 2]),
    );
    assert!(f1.structural_eq(&f2));

    // joint probabilities with different orders
    let f1 = Form::prob(vec![0, 1, 2]);
    let f2 = Form::prob(vec![2, 0, 1]);
    assert!(f1.structural_eq(&f2), "{:?} should equal {:?}", f1, f2);

    // test nested unorder probabilities
    let f1 = Form::product(vec![
        Form::prob(vec![0, 3]),
        Form::prob(vec![4]),
        Form::prob(vec![6, 7]),
    ]);
    let f2 = Form::product(vec![
        Form::prob(vec![6, 7]),
        Form::prob(vec![3, 0]),
        Form::prob(vec![4]),
    ]);
    assert!(f1.structural_eq(&f2), "{:?} should equal {:?}", f1, f2);

    // test involving quotients of marginals
    let f1 = Form::quotient(
        Form::marginal(
            set![0, 1],
            Form::product(vec![
                Form::prob(vec![0, 1, 2]),
                Form::prob(vec![3, 4, 5]),
                ])),
        Form::prob(vec![0, 1, 2]),
    );
    let f2 = Form::quotient(
        Form::marginal(
            set![1, 0],
            Form::product(vec![
                Form::prob(vec![3, 4, 5]),
                Form::prob(vec![0, 1, 2]),
                ])),
        Form::prob(vec![0, 1, 2]),
    );
    assert!(f1.structural_eq(&f2), "{:?} should equal {:?}", f1, f2);  

    // test involving quotients of marginals
    let f1 = Form::quotient(
        Form::marginal(
            set![0, 1],
            Form::product(vec![
                Form::prob(vec![0, 1, 2]),
                Form::prob(vec![3, 4, 5]),
                ])),
        Form::prob(vec![0, 1, 2]),
    );
    let f2 = Form::quotient(
        Form::marginal(
            set![1, 0],
            Form::product(vec![
                Form::prob(vec![4, 5, 3]),
                Form::prob(vec![0, 1, 2]),
                ])),
        Form::prob(vec![0, 1, 2]),
    );
    assert!(f1.structural_eq(&f2), "{:?} should equal {:?}", f1, f2);   

}