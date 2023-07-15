use cute::c;
use crate::{
    graph::{Node, Graph},
    form::Form,
    model::Model,
    utils::{
        defaults::{Set, Map},
        set_utils::{union, intersection, difference, make_set},
    }
};

pub fn id_no_simplify(model: &Model, y: &Set<Node>, x: &Set<Node>) -> Form {
    let observed = model.get_observed();
    if observed.is_empty() {
        return _id(model, y, x, model.p());
    } else {
        let model_hidden = &model.hide(&observed);
        let p_prime = _id(
            &model_hidden,
            &union(y, &observed),
            x,
            model_hidden.p()
        );
        let p = Form::quotient(
            p_prime.to_owned(),
            Form::marginal(y.to_owned(), p_prime)
        );
        return p;
    };
}

pub fn id(model: &Model, y: &Set<Node>, x: &Set<Node>) -> Form {
    id_no_simplify(model, y, x).simplify()
}

fn _id(model: &Model, y: &Set<Node>, x: &Set<Node>, p: Form) -> Form {

    let v = model.get_nodes();
    
    // step 1
    // in the case of no intervention, return the marginal
    if x.len() == 0 {
        return Form::marginal(difference(v, &y), p);
    }

    // step 2
    // restrict graph to y and ancestors of y
    {
        let ancestors_y_and_y = union(&model.dag.ancestors_set(&y), &y);
        if v != &ancestors_y_and_y {
                // replace with length equality check?
            let subg = model.subgraph(&ancestors_y_and_y);
            return _id(
                    &subg,
                    y,
                    &intersection(x, &ancestors_y_and_y),
                    Form::marginal(difference(v, &ancestors_y_and_y), p)
                );
        }
    }

    // step 3
    // force an action where this would have no effect on y
    {
        let a_y_do_x = model.dag
            .r#do(x)
            .ancestors_set(y);
        // simplify w? do we need to subtract x?
        let w = difference(v, &union(x, &union(&a_y_do_x, &y)));
        if !w.is_empty() {
            return _id(model, y, &union(&x, &w), p);
        }
    }

    // step 4
    // c_component factorization of the problem

    let less_x = model.subgraph(&difference(v, &x));
    let mut c_components_less_x = less_x
        .confounded
        .c_components();
    
    if c_components_less_x.len() > 1 {
        return Form::marginal(
            difference(v, &union(&y, &x)),
                // will this difference ever contain anything?
            Form::product(c![
                _id(model, &s_i, &difference(v, &s_i), p.clone()),
                for s_i in c_components_less_x
            ])
        );
    }

    // step 5
    // fail if a hedge is discovered
    let c_components = model.confounded.c_components();
    if c_components.len() == 1 {
        return Form::Hedge;
    }

    // homestretch woot
    let s = c_components_less_x.pop()
        .expect("no c_components found in derived model");
    for s_prime in c_components {
        if s.is_subset(&s_prime) {
            // step 6
            // if x is contained in isolated c_components, condition and win
            if s.len() == s_prime.len() {
                return Form::marginal(
                    difference(&s, y),
                    Form::factorize_subset(model.order_vec(), p, &s)
                );
            // step 7
            // partition x into confounded and uncounfounded
            } else {
                return _id(
                    &model.subgraph(&s_prime),
                    y,
                    &intersection(&x, &s_prime),
                    Form::factorize_subset(model.order_vec(), p, &s_prime)
                );
            }
        }
    }

    panic!("id assumptions violated");
    
}
