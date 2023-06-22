#![cfg(test)]

use super::id;
use crate::{
    model::{
        Model,
        examples::frontdoor_model
    },
    utils::defaults::{set, Set},
    form::{Form, HEDGE},
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
    let estimand = id(&model, &set![2], &set![1]).simplify();
    let answer = Form::marginal(set![0], Form::product(vec![
        Form::prob(vec![0]),
        Form::cond_prob(vec![2], vec![0, 1]),
    ])).cond_expand().simplify();

    assert_eq!(estimand, answer);
}

#[test]
fn test_frontdoor() {
    let model = frontdoor_model();
    let estimand = id(&model, &set![2], &set![0]);
    let answer = Form::marginal(set![1],
        Form::product(vec![
            Form::cond_prob(vec![1], vec![0]),
            Form::marginal(set![0],
                Form::product(vec![
                    Form::prob(vec![0]),
                    Form::cond_prob(vec![2], vec![0, 1]),
                ])
            )
        ])
    ).cond_expand().simplify();
    assert_eq!(estimand.simplify(), answer);
}

#[test]
fn test_bowgraph () {
    let model = Model::from_elems(
        vec![(1, vec![0])],
        vec![(0, 1)]
    );
    assert_eq!(id(&model, &set!(1), &set![0]).simplify(), Form::Hedge);
}

#[test]
fn test_shp_hedge () {
    let model = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1]),
            (3, vec![0]),
            (4, vec![3]),

        ],
        vec![
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 3)
        ]
    );

    assert_eq!(id(&model, &set![2, 4], &set![1]).simplify(), Form::Hedge);
}

#[test]
fn test_shp_good () {
    // Example he keeps using in the paper
    // 0 <- 1
    // 2 <- 1
    // 4 <- 3
    // 0 <> 2
    // 0 <> 3
    // 0 <> 4
    // 1 <> 3
    let model = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1]),
            (4, vec![3]),

        ],
        vec![
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 3)
        ]
    );

    assert_ne!(id(&model, &set![2, 4], &set![1]).simplify(), Form::Hedge);
}

#[test]
fn test_shp_p14() {
    // Example from p. 14 of the dissertation, should all identify

    // 0 <- 1
    let model1 = Model::from_elems(
        vec![(1, vec![0])],
        vec![]
    );
    assert_ne!(id(&model1, &set![1], &set![0]).simplify(), Form::Hedge, "example 1");

    // 1 <- 0
    // 2 <- [0, 1]
    // 1 <> 2
    let model2 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![0, 1]),
        ],
        vec![(1, 2)]
    );
    assert_ne!(id(&model2, &set![2], &set![0]).simplify(), Form::Hedge, "example 2");

    // 0 <- 1
    // 2 <- [1, 0]
    // 1 <> 2
    let model3 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1, 0]),
        ],
        vec![(1, 2)]
    );
    assert_ne!(id(&model3, &set![2], &set![0]).simplify(), Form::Hedge, "example 3");

    // 0 <- 1
    // 2 <- [0, 1]
    // 0 <> 1
    let model4 = Model::from_elems(
        vec![
            (0, vec![1]),
            (2, vec![0, 1]),
        ],
        vec![(0, 1)]
    );
    assert_ne!(id(&model4, &set![2], &set![0]).simplify(), Form::Hedge, "example 4");

    // 1 <- 0
    // 2 <- 1
    // 0 <> 2
    let model5 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1]),
        ],
        vec![(0, 2)]
    );
    assert_ne!(id(&model5, &set![2], &set![0]).simplify(), Form::Hedge, "example 5");

    // 1 <- 0
    // 2 <- 1
    // 3 <- [0, 1, 2]
    // 0 <> 2
    // 1 <> 3
    let model6 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1]),
            (3, vec![0, 1, 2]),
        ],
        vec![(0, 2), (1, 3)]
    );
    assert_ne!(id(&model6, &set![3], &set![0]).simplify(), Form::Hedge, "example 6");

    // 0 <- 2
    // 1 <- [0, 2]
    // 3 <- 2
    // 4 <- [1, 3]
    // 0 <> 2
    // 0 <> 4
    // 0 <> 3
    // 2 <> 4
    let model7 = Model::from_elems(
        vec![
            (0, vec![2]),
            (1, vec![0, 2]),
            (3, vec![2]),
            (4, vec![1, 3]),
        ],
        vec![(0, 2), (0, 4), (0, 3), (2, 4)]
    );
    assert_ne!(id(&model7, &set![4], &set![0]).simplify(), Form::Hedge, "example 7");

}

fn test_shp_p13 () {
    // Example from p. 13

    // 1 <- 0
    // 0 <> 1
    let model1 = Model::from_elems(
        vec![(1, vec![0])],
        vec![(0, 1)]
    );
    assert_eq!(id(&model1, &set![1], &set![0]).simplify(), Form::Hedge, "example 1");

    // 1 <- 0
    // 2 <- 1
    // 0 <> 1
    let model2 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1]),
        ],
        vec![(0, 1)]
    );
    assert_eq!(id(&model2, &set![2], &set![0]).simplify(), Form::Hedge, "example 2");

    // 1 <- 0
    // 2 <- 1, 0
    // 0 <> 1
    let model3 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1, 0]),
        ],
        vec![(0, 1)]
    );
    assert_eq!(id(&model3, &set![2], &set![0]).simplify(), Form::Hedge, "example 3");

    // 2 <- 1, 0
    // 0 <> 1
    // 1 <> 2
    let model4 = Model::from_elems(
        vec![
            (2, vec![1, 0]),
        ],
        vec![(0, 1), (1, 2)]
    );
    assert_eq!(id(&model4, &set![2], &set![0]).simplify(), Form::Hedge, "example 4");

    // 0 <- 1
    // 2 <- 0
    // 0 <> 1
    // 1 <> 2
    let model5 = Model::from_elems(
        vec![
            (0, vec![1]),
            (2, vec![0]),
        ],
        vec![(0, 1), (1, 2)]
    );
    assert_eq!(id(&model5, &set![2], &set![0]).simplify(), Form::Hedge, "example 5");

    // 1 <- 0
    // 2 <- 1
    // 0 <> 2
    // 1 <> 2
    let model6 = Model::from_elems(
        vec![
            (1, vec![0]),
            (2, vec![1]),
        ],
        vec![(0, 2), (1, 2)]
    );
    assert_eq!(id(&model6, &set![2], &set![0]).simplify(), Form::Hedge, "example 6");

    // 1 <- 0
    // 3 <- 1, 2
    // 0 <> 2
    // 1 <> 2
    let model7 = Model::from_elems(
        vec![
            (1, vec![0]),
            (3, vec![1, 2]),
        ],
        vec![(0, 2), (1, 2)]
    );
    assert_eq!(id(&model7, &set![3], &set![0]).simplify(), Form::Hedge, "example 7");

    // 0 <- 1
    // 2 <- 0
    // 3 <- 2
    // 1 <> 0, 2, 3
    // 0 <> 3
    let model8 = Model::from_elems(
        vec![
            (0, vec![1]),
            (2, vec![0]),
            (3, vec![2]),
        ],
        vec![(1, 0), (1, 2), (1, 3), (0, 3)]
    );
    assert_eq!(id(&model8, &set![3], &set![0]).simplify(), Form::Hedge, "example 8");


}