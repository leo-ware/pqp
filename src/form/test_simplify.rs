#![cfg(test)]
use crate::utils::defaults::{set, Set};
use super::{
    simplify::{
        simplify,
        simplify_product,
        simplify_quotient,
        simplify_marginal,
        promote_hedge
    },
    form::{one, HEDGE},
    Form,
};

#[test]
fn test_simplify_marginal() {
    let f = Form::marginal(set![0, 1], Form::prob(vec![0, 1, 2]));
    let simple = Form::prob(vec![2]);
    assert_eq!(simplify_marginal(&f), simple);

    // ensure it merges with nested marginals
    let f = Form::marginal(set![0, 1], Form::marginal(set![2], Form::prob(vec![3])));
    let simple = Form::marginal(set![0, 1, 2], Form::prob(vec![3]));
    assert_eq!(simplify_marginal(&f), simple);

    // ensure it does nothing if inside is not a probability or marginal
    let f = Form::marginal(set![0, 1], Form::product(vec![Form::prob(vec![0, 1, 2])]));
    let simple = Form::marginal(set![0, 1], Form::product(vec![Form::prob(vec![0, 1, 2])]));
    assert_eq!(simplify_marginal(&f), simple);
}

#[test]
fn test_simplify_product () {

    // merging with nested quotients
    let f = Form::product(vec![
        Form::product(vec![
            Form::prob(vec![0, 3])
        ]),
        Form::quotient(
            Form::prob(vec![4]),
            Form::prob(vec![6, 7]),
        ),
    ]);
    let simple = Form::quotient(
        Form::product(vec![Form::prob(vec![0, 3]), Form::prob(vec![4])]),
        Form::prob(vec![6, 7])
    );
    assert_eq!(simplify_product(&f), simple, "failed with nested quotients");

    // ensure it merges with nested products
    let f = Form::product(vec![
        Form::product(vec![
            Form::prob(vec![0, 3])
        ]),
        Form::product(vec![
            Form::prob(vec![4]),
            Form::prob(vec![6, 7]),
        ]),
    ]);
    let simple = Form::product(vec![
        Form::prob(vec![0, 3]),
        Form::prob(vec![4]),
        Form::prob(vec![6, 7]),
    ]);
    assert_eq!(simplify_product(&f), simple, "failed with nested products");

    // nested marginals
    let f = Form::product(vec![
        Form::product(vec![
            Form::prob(vec![0, 3])
        ]),
        Form::marginal(set![0, 1], Form::prob(vec![0, 1, 2])),
    ]);
    let simple = Form::product(vec![
        Form::prob(vec![0, 3]),
        Form::marginal(set![0, 1], Form::prob(vec![0, 1, 2])),
    ]);
    assert_eq!(simplify_product(&f), simple, "failed with nested marginals");
}

#[test]
fn test_simplify_quotient () {
    // ensure it merges with nested products
    let f = Form::quotient(
        Form::quotient(
                Form::prob(vec![0, 3]),
                Form::product(vec![
                    Form::prob(vec![4]),
                    Form::prob(vec![6, 7]),
                ]),
            ),
        Form::quotient(Form::prob(vec![8]), Form::prob(vec![9]))
    );
    let simple = Form::quotient(
        Form::product(vec![
            Form::prob(vec![0, 3]),
            Form::prob(vec![9]),
        ]),
        Form::product(
            vec![
                Form::prob(vec![4]),
                Form::prob(vec![6, 7]),
                Form::prob(vec![8]),
            ]
        )
    );
    assert_eq!(simplify_quotient(&f), simple, "failed with nested quotients top/bottom");

    // ensure it cancels identical terms
    let f = Form::quotient(
        Form::product(vec![
            Form::prob(vec![0]),
            Form::prob(vec![1]),
        ]),
        Form::prob(vec![1]),
    );
    let simple = Form::prob(vec![0]);
    assert_eq!(simplify_quotient(&f), simple, "failed to cancel");

    let f = Form::quotient(
        Form::product(vec![
            Form::prob(vec![0, 1, 2]),
            Form::prob(vec![1, 2]),
            Form::prob(vec![2]),
        ]),
        Form::product(vec![
            Form::prob(vec![2, 1]),
            Form::prob(vec![2]),
        ])
    );
    let simple = Form::prob(vec![0, 1, 2]);
    assert_eq!(simplify_quotient(&f), simple, "failed to cancel (#2)");
}

#[test]
fn test_simplify () {
    // test two nested quotients
    let f = Form::quotient(
        Form::quotient(
            Form::prob(vec![0]),
            Form::prob(vec![1]),
        ),
        Form::prob(vec![2, 3])
    );
    let simplified = simplify(&f).sorted();
    let simple = Form::quotient(
        Form::prob(vec![0]),
        Form::product(vec![
            Form::prob(vec![1]),
            Form::prob(vec![2, 3]),
        ])
    ).sorted();
    assert_eq!(simplified, simple, "{:?} should equal {:?}", simplified, simple);

    // test three nested quotients
    let f = Form::quotient(
        Form::quotient(
            Form::quotient(
                Form::prob(vec![0]),
                Form::prob(vec![1]),
            ),
            Form::prob(vec![2]),
        ),
        one()
    );
    let simplified = simplify(&f).sorted();
    let simple = Form::quotient(
        Form::prob(vec![0]),
        Form::product(vec![
            Form::prob(vec![1]),
            Form::prob(vec![2]),
        ])
    );
    assert_eq!(simplified, simple, "{:?} should equal {:?}", simplified, simple);

    // merging with nested quotients
    let f = Form::quotient(
        Form::product(vec![
                Form::prob(vec![0, 3]),
                Form::quotient(
                    Form::prob(vec![4]),
                    Form::prob(vec![6, 7]),
                ),
            ]),
        Form::prob(vec![8, 9])
    );
    let simplified = simplify(&f).sorted();
    let simple = Form::quotient(
        Form::product(vec![
            Form::prob(vec![0, 3]),
            Form::prob(vec![4]),
        ]),
        Form::product(vec![
            Form::prob(vec![6, 7]),
            Form::prob(vec![8, 9]),
        ])
    );
    assert_eq!(simplified, simple, "{:?} should equal {:?}", simplified, simple);
}

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

