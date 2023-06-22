use super::form::{Form, one};
use crate::{
    P,
    api::wrapper::ModelWrapper,
    identification::id_no_simplify,
    model::examples::frontdoor_model,
    utils::defaults::{set, Set},
    graph::make_nodes,
};

#[test]
fn test_sort() {
    let f = Form::prob(vec![1, 2, 0]).sorted();
    let s = Form::prob(vec![0, 1, 2]);
    assert_eq!(f, Form::prob(vec![0, 1, 2]), "{:?} should equal {:?}", f, s);
}

#[test]
fn test_structural_eq() {
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
            Form::product(vec![Form::prob(vec![0, 1, 2]), Form::prob(vec![3, 4, 5])]),
        ),
        Form::prob(vec![0, 1, 2]),
    );
    let f2 = Form::quotient(
        Form::marginal(
            set![1, 0],
            Form::product(vec![Form::prob(vec![3, 4, 5]), Form::prob(vec![0, 1, 2])]),
        ),
        Form::prob(vec![0, 1, 2]),
    );
    assert!(f1.structural_eq(&f2), "{:?} should equal {:?}", f1, f2);

    // test involving quotients of marginals
    let f1 = Form::quotient(
        Form::marginal(
            set![0, 1],
            Form::product(vec![Form::prob(vec![0, 1, 2]), Form::prob(vec![3, 4, 5])]),
        ),
        Form::prob(vec![0, 1, 2]),
    );
    let f2 = Form::quotient(
        Form::marginal(
            set![1, 0],
            Form::product(vec![Form::prob(vec![4, 5, 3]), Form::prob(vec![0, 1, 2])]),
        ),
        Form::prob(vec![0, 1, 2]),
    );
    assert!(f1.structural_eq(&f2), "{:?} should equal {:?}", f1, f2);
}

#[test]
fn test_factorize_subset() {
    let model = frontdoor_model();
    let order = model.order_vec();
    let p = model.p();

    let f = Form::factorize_subset(order, p, &set![0, 2]);
    let ans = Form::quotient(
        Form::product(vec![
            Form::prob(vec![0]),
            Form::cond_prob(vec![0, 1, 2], vec![]),
        ]),
        Form::prob(vec![0, 1]),
    );

    assert_eq!(f.simplify(), ans.simplify());
}

#[test]
fn test_p_macro () {
    if let [a, b, c] = make_nodes(3)[..] {
        assert_eq!(P!(a, b), Form::prob(vec![a, b]));
        assert_eq!(P!(a, b | c), Form::cond_prob(vec![a, b], vec![c]));
        assert_eq!(P!(), one());
    } else {
        panic!("make_nodes(3) should return 3 nodes");
    }
}

#[test]
fn test_infix() {
    if let [a, b, c] = make_nodes(3)[..] {
        assert_eq!(P!(a) * P!(b), Form::product(vec![P!(a), P!(b)]));
        assert_eq!(P!(a) / P!(b), Form::quotient(P!(a), P!(b)));
        assert_eq!(P!(a) * P!(b) * P!(c), Form::product(vec![P!(a), P!(b), P!(c)]));
        assert_eq!(P!(a) * P!(b) / P!(c), Form::quotient(Form::product(vec![P!(a), P!(b)]), P!(c)));
    } else {
        panic!("make_nodes(3) should return 3 nodes");
    }
}