use cute::c;
use crate::{
    defaults::{Set, Map},
    graph::{Node, Graph},
    form::Form,
    set_utils::{union, intersection, difference, make_set},
    model::Model,
};

pub fn id(model: &Model, y: &Set<Node>, x: &Set<Node>, p: Form) -> Form {
    let v = model.get_nodes();
    
    // step 1
    if x.len() == 0 {
        return Form::marginal(difference(v, &y), p);
    }

    // step 2
    let ancestors_y = model.dag.ancestors_set(&y);
    if v != &ancestors_y {
            // replace with length equality check?
        let subg = model.subgraph(&ancestors_y);
        return id(
                &subg,
                y,
                &intersection(x, &ancestors_y),
                Form::marginal(difference(v, &ancestors_y), p)
            );
    }

    // step 3
    let a_y_intervene = model.dag
        .r#do(x)
        .ancestors_set(y);
    // simplify w? do we need to subtract x?
    let w = difference(&difference(v, x), &a_y_intervene);
    if !w.is_empty() {
        return id(model, y, &union(&x, &w), p);
    }

    // step 4
    let c_components_less_x = model
        .subgraph(&difference(v, &x))
        .confounded
        .c_components();
    
    if c_components_less_x.len() > 1 {
        return Form::marginal(
            difference(v, &union(&y, &x)),
                // will this difference ever contain anything?
            Form::product(c![
                id(model, &s_i, &difference(v, &s_i), p.clone()),
                for s_i in c_components_less_x
            ])
        );
    }

    // step 5
    let mut c_components = model.confounded.c_components();
    if c_components.len() == 1 {
        return Form::Fail;
    }

    // homestretch woot
    let s = c_components.pop().expect("arggg");
    for s_prime in c_components_less_x {
        if s.is_subset(&s_prime) {
            // step 6
            if s.len() == s_prime.len() {
                return Form::marginal(
                    difference(&s, y),
                    Form::factorize(model.order(), p)
                );
            // step 7
            } else {
                // let w = &union(&x, &s_prime);
                return id(
                    &model.subgraph(&s_prime),
                    y,
                    &intersection(&x, &s_prime),
                    Form::factorize(model.order(), p)
                );
            }
        }
    }

    panic!("id assumptions violated");
    
}