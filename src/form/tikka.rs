use crate::{
    utils::{defaults::{Map, Set}, set_utils::{union, difference, copy_set, make_set, powerset, symmetric_difference}},
    graph::Node,
    model::{Model, order::Order}, set,
};

pub struct Atomic {
    s: Set<Node>,
    t: Vec<(Node, Set<Node>)>,
}

pub struct Expression {
    s: Set<Node>,
    b: Box<Vec<Expression>>,
    a: Atomic,
}

// fn index_of (a: Atomic, j: i32) -> i32 {
//     todo!();
// }

// fn get_missing (a: Atomic, g: Model, j: i32) -> Set<Node> {
//     todo!();
// }

fn insert (j: &Set<Node>, j_cond: &Set<Node>, m: &Node, s: &Node, model: &Model, pi: &Order) -> (Set<Node>, Set<Node>, Set<Node>) {
    let an_m_inc = pi.set_predecessors(j).unwrap().iter().cloned().collect();
    let g = difference(&an_m_inc, &model.ancestors_inc(*m));
    // ???
    todo!();
}

fn join (j_vars: &Set<Node>, j_conditional: &Set<Node>, v: &Node, v_conditional: &Set<Node>, summation_var: &Node, nonpresent_vars: &Set<Node>, model: &Model, pi: &Order) -> (Set<Node>, Set<Node>, Set<Node>) {
    if j_vars.is_empty() {
        return (Set::from([*v]), copy_set(v_conditional), Set::new());
    }

    let an_v_inc = model.ancestors_inc(*v);
    let an_v = difference(&an_v_inc, &set![*v]);

    let pi_before_j = make_set(pi.set_predecessors(j_vars).unwrap().into_iter());
    let g = difference(&pi_before_j, &an_v_inc);

    for p_i in powerset(&g) {
        let a = symmetric_difference(&union(&an_v_inc, &p_i), j_conditional);
        let b = symmetric_difference(&union(&an_v, &p_i), v_conditional);

        if model.cond(&difference(j_conditional, &a)).independent(&j_vars, &a) &&
            model.cond(&difference(v_conditional, &b)).independent(&set![*v], &b) {
            
            return (union(j_vars, &set![*v]), union(&an_v, &p_i), set![]);
        }
    }

    if !nonpresent_vars.is_empty() {
        for m in nonpresent_vars {
            if j_conditional.contains(m) && !v_conditional.contains(m) {
                let (j_new, j_cond_new, r) = insert(j_vars, j_conditional, m, summation_var, model, pi);
                if j_vars.is_subset(&j_new) {
                    return (j_new, j_cond_new, r);
                }
            }
        }
    }

    return (j_vars.clone(), j_conditional.clone(), set![]);
}

// fn factorize ( )

// fn simplify (a: Atomic, g: Model, pi: Map<Node, i32>) -> Atomic {
//     let mut j: i32 = 0;
//     while j < a.s.len().try_into().unwrap() {
//         let mut B = a;
//         let mut J = Set::new();
//         let mut D = Set::new();
//         let mut R = Set::new();
//         let mut I = Vec::new();
//         j += 1;
//         let S_j: Node;

//         let mut i = index_of(a, j);
//         let mut M = get_missing(a, g, j);
//         let mut k = 1;

//         while k <= i {
//             let V_k: Node;
//             let C_k: Set<Node>;
//             let (J_new, D_new, R_new) = join(J, D, V_k, C_k, S_j, M, g, pi);
//             if J_new.is_subset(J) {
//                 break;
//             } else {
//                 J = J_new;
//                 D = D_new;
//                 if !R_new.is_empty() {
//                     R = union(&R, &R_new);
//                     I.push(D);
//                     M = difference(&M, &R_new);
//                 } else {
//                     k += 1;
//                 }
//             }
//         }

//         if k = i + 1 {
//             let A_new = factorize();
//         }

//     }

//     todo!();
// }