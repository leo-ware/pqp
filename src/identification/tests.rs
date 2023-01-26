#![cfg(test)]

use super::id;
use crate::{
    model::{
        Model,
        examples::frontdoor_model
    },
    utils::defaults::{set, Set}, form::{Form, HEDGE},
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