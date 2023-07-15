#![cfg(test)]

use crate::{
    model::examples::frontdoor_model,
    identification::id,
    utils::defaults::{set, Set},
};

#[test]
fn do_stuff() {
    let fd = frontdoor_model();
    println!("{:?}", fd);
    println!("{:?}", id(&fd, &set!(2), &set!(0)));
}

// "Marginal({1}, Product([Marginal({}, Product([Quotient(Marginal({}, Marginal({2}, P([2, 0, 1], []))), Marginal({1}, Marginal({2}, P([2, 0, 1], [])))), Quotient(Marginal({1}, Marginal({2}, P([2, 0, 1], []))), Marginal({1, 0}, Marginal({2}, P([2, 0, 1], []))))])), Marginal({}, Product([Quotient(Marginal({}, P([2, 0, 1], [])), Marginal({2}, P([2, 0, 1], []))), Quotient(Marginal({2}, P([2, 0, 1], [])), Marginal({1, 2}, P([2, 0, 1], []))), Quotient(Marginal({1, 2}, P([2, 0, 1], [])), Marginal({1, 0, 2}, P([2, 0, 1], [])))]))]))"