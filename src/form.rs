use crate::{set_utils::{difference, union, make_set}, graph::Node};
use crate::defaults::Set;

#[derive(Debug, Clone)]
pub enum Form {
    Marginal(Set<Node>, Box<Form>),
    Product(Vec<Form>),
    Quotient(Box<Form>, Box<Form>),
    P(Vec<Node>, Vec<Node>),
    Fail
}

impl<'a> Form {
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
            Form::Fail => Set::new(),
        }
    }

    pub fn factorize(order: Vec<Node>, p: Form) -> Form {
        let mut free = Form::free(&p);
        let mut terms = Vec::new();

        for nxt in order.iter().enumerate() {
            let (i, v_i) = nxt;
            let v: Set<Node> = [*v_i].into_iter().collect();
            let pred = make_set((&order[i..]).iter().map(|e| *e));
            let unbound = difference(&free, &union(&pred, &v));
            let term = Form::quotient(
                Form::marginal(unbound.clone(), p.clone()),
                Form::marginal(union(&unbound, &v), p.clone())
            );
            terms.push(term);
        }
        
        return Form::product(terms);
    }
}