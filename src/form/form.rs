use core::num;
use cute::c;

use crate::{
    utils::{
        set_utils::{difference, union, make_set},
        defaults::Set,
    },
    graph::Node
};

use super::simplify;

pub static HEDGE: Form = Form::Hedge;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AbstractForm<T: Eq + std::hash::Hash> {
    Marginal(Set<T>, Box<AbstractForm<T>>),
    Product(Vec<AbstractForm<T>>),
    Quotient(Box<AbstractForm<T>>, Box<AbstractForm<T>>),
    P(Vec<T>, Vec<T>),
    Hedge
}

pub type Form = AbstractForm<Node>;

impl Form {
    pub fn marginal(over: Set<Node>, exp: Form) -> Form {
        Form::Marginal(over, Box::new(exp))
    }

    pub fn product(forms: Vec<Form>) -> Form {
        Form::Product(forms)
    }

    pub fn quotient(num: Form, denom: Form) -> Form {
        Form::Quotient(Box::new(num), Box::new(denom))
    }

    pub fn prob(vars: Vec<Node>) -> Form {
        Form::P(vars, vec![])
    }

    pub fn cond_prob(vars: Vec<Node>, given: Vec<Node>) -> Form {
        Form::P(vars, given)
    }

    pub fn free<'b>(form: &'b Form) -> Set<Node> {
        match form {
            Form::Marginal(sub, exp) => 
                difference(&Form::free(&**exp), &sub),
            Form::Quotient(numer, denom) =>
                union(&Form::free(&**numer), &Form::free(&**denom)),
            Form::P(vars, given) => {
                let mut set = Set::new();
                vars.iter().for_each(|e| {set.insert(*e);});
                given.iter().for_each(|e| {set.insert(*e);});
                return set;
            },
            Form::Product(exprs) => {
                let mut set = Set::new();
                for expr in exprs.iter() {
                    set.extend(Form::free(expr));
                }
                return set;
            },
            Form::Hedge => Set::new(),
        }
    }

    /// Finds P(subset | pred(subset)) in terms of p, where pred(x) is the
    /// predecessors of x in order.
    pub fn factorize_subset(order: Vec<Node>, p: Form, subset: &Set<Node>) -> Form {
        let mut free = Form::free(&p);
        let mut terms = Vec::new();

        for nxt in order.iter().enumerate() {
            let (i, v_i) = nxt;
            if subset.contains(v_i) {
                let v: Set<Node> = [*v_i].into_iter().collect();
                let pred = make_set((&order[i..]).iter().map(|e| *e));
                let unbound = difference(&free, &union(&pred, &v));
                let term = Form::quotient(
                    Form::marginal(unbound.clone(), p.clone()),
                    Form::marginal(union(&unbound, &v), p.clone())
                );
                terms.push(term);
            }
        }
        
        return Form::product(terms);
    }

    /// Factorize a form with respect to a given order
    pub fn factorize(order: Vec<Node>, p: Form) -> Form {
        let subset = make_set(order.iter().map(|e| *e));
        Form::factorize_subset(order, p, &subset)
    }

    /// determine if a form contains a hedge
    pub fn contains_hedge(&self) -> bool {
        match self {
            Form::Marginal(_, exp) => exp.contains_hedge(),
            Form::Product(exprs) => {
                for expr in exprs {
                    if expr.contains_hedge() {
                        return true;
                    }
                }
                return false;
            },
            Form::Quotient(numer, denom) => {
                numer.contains_hedge() || denom.contains_hedge()
            },
            Form::P(_, _) => false,
            Form::Hedge => true,
        }
    }

    pub fn form_type(form: &Self) -> i8 {
        match form {
            Form::Marginal(_, _) => 0,
            Form::Product(_) => 1,
            Form::Quotient(_, _) => 2,
            Form::P(_, _) => 3,
            Form::Hedge => 4,
        }
    }

    fn do_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        let s_val = Form::form_type(self);
        let o_val = Form::form_type(other);

        if s_val < o_val {
            return Some(std::cmp::Ordering::Less);
        } else if s_val > o_val {
            return Some(std::cmp::Ordering::Greater);
        }

        match (self, other) {
            (Form::Marginal(s_over, s_exp), Form::Marginal(o_over, o_exp)) => {
                if s_over.len() == o_over.len() {
                    s_exp.partial_cmp(o_exp)
                } else {
                    s_over.len().partial_cmp(&o_over.len())
                }
            },
            (Form::Product(s_exprs), Form::Product(o_exprs)) => {
                s_exprs.partial_cmp(o_exprs)
            },
            (Form::Quotient(s_numer, s_denom), Form::Quotient(o_numer, o_denom)) => {
                if s_numer == o_numer {
                    s_denom.partial_cmp(o_denom)
                } else {
                    s_numer.partial_cmp(o_numer)
                }
            },
            (Form::P(s_vars, s_given), Form::P(o_vars, o_given)) => {
                if s_vars == o_vars {
                    s_given.partial_cmp(o_given)
                } else {
                    s_vars.partial_cmp(o_vars)
                }
            },
            _ => Some(std::cmp::Ordering::Equal),
        }
    }

    /// applies form_map with the same func to child expressions, then applies func to self
    pub fn map (&self, func: fn(&Form) -> Form) -> Form {
        let mapped = match self {
            Form::Marginal(over, exp)
                => Form::marginal(over.clone(), exp.map(func)),
            Form::Product(exprs)
                => Form::product(exprs.iter().map(|e| e.map(func)).collect()),
            Form::Quotient(numer, denom)
                => Form::quotient(numer.map(func), denom.map(func)),
            _ => self.to_owned(),
        };
        return func(&mapped);
    }

    /// recursively sorts expressions, returning a new form
    pub fn sorted(&self) -> Form {
        match self {
            Form::Marginal(over, exp) => {
                Form::marginal(over.to_owned(), exp.sorted())
            },
            Form::Product(exprs) => {
                let mut exprs: Vec<Form> = exprs
                    .iter()
                    .map(|e| e.sorted())
                    .collect();
                exprs.sort();
                Form::product(exprs)
            },
            Form::Quotient(numer, denom) => {
                Form::quotient(numer.sorted(), denom.sorted())
            },
            Form::P(vars, cond) => {
                let mut vars = vars.to_owned();
                let mut cond = cond.to_owned();
                vars.sort();
                cond.sort();
                Form::cond_prob(vars, cond)
            }
            _ => self.to_owned(),
        }
    }

    pub fn cond_expand(&self) -> Form {
        self.map(|f| {
            match f {
                Form::P(vars, cond) => {
                    Form::quotient(
                        Form::prob(
                            vars.iter().cloned().chain(cond.iter().cloned()).collect()
                        ),
                        Form::prob(cond.to_owned())
                    )
                },
                _ => f.to_owned(),
            }
        })
    }

    pub fn structural_eq(&self, other: &Form) -> bool {
        self.sorted() == other.sorted()
    }

    /// Sorts and simplifies a form. Suitable for structural equality checks.
    pub fn simplify(&self) -> Form {
        simplify(&self.sorted())
    }
}

impl PartialOrd for Form {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(Form::cmp(&self, other))
    }
}

impl Ord for Form {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        Form::do_cmp(&self, other).unwrap()
    }   
}

pub fn one () -> Form {
    Form::prob(vec![])
}
