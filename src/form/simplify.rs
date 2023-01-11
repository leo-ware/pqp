
use core::num;
use std::{
    iter::Product,
    convert::identity,
};

use crate::{
    utils::{
        set_utils::{difference, make_set, union},
        defaults::Set,
        remove_duplicates_sorted,
    },
    graph::Node
};

use super::form::{Form, one, HEDGE};

pub fn promote_hedge(f: &Form) -> &Form {
    if f.contains_hedge() {
        &HEDGE
    } else {
        f
    }
}

/// Simplify a marginal expression.
/// Will reduce terms in a joint probability if it finds one.
pub fn simplify_marginal(f: &Form) -> Form {
    if let Form::Marginal(over, exp) = f {
        let exp_content = *exp.to_owned();

        if over.is_empty() {
            return exp_content;
        } else if let Form::Marginal(over2, exp2) = exp_content {
            return Form::marginal(union(&over, &over2), *exp2);
        } else if let Form::P(vars, cond) = exp_content {
            let vars_set: Set<Node> = vars.iter().cloned().collect();
            let new_over = difference(&over, &vars_set);
            let new_vars = difference(&vars_set, &over);
            let new_p = Form::cond_prob(new_vars.iter().cloned().collect(), cond);

            if !new_over.is_empty() {
                return Form::marginal(new_over, new_p);
            } else {
                return new_p;
            }
        }
    }

    return f.to_owned();
}

/// Simplify a product of expressions.
/// After simplification, product will not contain any product, quotient, or one.
pub fn simplify_product(f: &Form) -> Form {
    if let Form::Product(exprs) = f {
        let mut numer = vec![];
        let mut denom = vec![];

        for exp in exprs.iter() {
            if let Form::Quotient(n, d) = exp {
                numer.push(*n.to_owned());
                denom.push(*d.to_owned());
            } else if let Form::Product(exprs2) = exp {
                for exp2 in exprs2.iter() {
                    if let Form::Quotient(n, d) = exp2 {
                        numer.push(*n.to_owned());
                        denom.push(*d.to_owned());
                    } else if exp != &one() {
                        numer.push(exp2.to_owned());
                    }
                }
            } else if exp != &one() {
                numer.push(exp.to_owned());
            }
        }

        let n_simple = if numer.len() > 1 {
            Form::product(numer)
        } else if numer.len() == 1 {
            numer[0].to_owned()
        } else {
            one()
        };

        let d_simple = if denom.len() > 1 {
            Form::product(denom)
        } else if denom.len() == 1 {
            denom[0].to_owned()
        } else {
            one()
        };

        if d_simple == one() {
            return n_simple;
        } else {
            return Form::quotient(n_simple, d_simple);
        }
    }

    return f.to_owned();
}

/// Simplify a quotient of expressions.
pub fn simplify_quotient (f: &Form) -> Form {
    if let Form::Quotient(numer, denom) = f {
        // collapse nested quotients
        let (top_numer, top_denom) = if let Form::Quotient(n, d) = *numer.to_owned() {
            (*n.to_owned(), *d.to_owned())
        } else {
            (*numer.to_owned(), one())
        };

        let (bottom_numer, bottom_denom) = if let Form::Quotient(n, d) = *denom.to_owned() {
            (*n.to_owned(), *d.to_owned())
        } else {
            (*denom.to_owned(), one())
        };

        let collapsed_numer = simplify_product(&Form::product(vec![top_numer, bottom_denom])).sorted();
        let collapsed_denom = simplify_product(&Form::product(vec![top_denom, bottom_numer])).sorted();

        // cancel duplicates
        let mut numer_vec = match collapsed_numer {
            Form::Product(exprs) => exprs,
            _ => vec![collapsed_numer],
        };
        numer_vec.sort_unstable();

        let mut denom_vec = match collapsed_denom {
            Form::Product(exprs) => exprs,
            _ => vec![collapsed_denom],
        };
        denom_vec.sort_unstable();

        let (numer_dedup, denom_dedup) = remove_duplicates_sorted(&numer_vec, &denom_vec);
        let numer_simple = simplify_product(&Form::product(numer_dedup));
        let denom_simple = simplify_product(&Form::product(denom_dedup));

        if denom_simple == one() {
            return numer_simple;
        } else {
            return Form::quotient(numer_simple, denom_simple);
        }
    }

    return f.to_owned();
}

/// Simplify a form (not recursive).
pub fn simplify_form(f: &Form) -> Form {
    let form_type = Form::form_type(&f);
    let func = match f {
        Form::Product(_) => simplify_product,
        Form::Quotient(_, _) => simplify_quotient,
        Form::Marginal(_, _) => simplify_marginal,
        _ => |g: &Form| {g.to_owned()},
    };
    let once = func(f);

    // if the form type hasn't changed, return the simplified form
    if Form::form_type(&once) == form_type {
        once
    } else {
        simplify_form(&once)
    }
}

/// Recursively simplify a form.
pub fn simplify(f: &Form) -> Form {
    let hedged = promote_hedge(f);
    if hedged == &HEDGE {
        return HEDGE.to_owned();
    } else {
        return f.map(simplify_form).sorted();
    }
}