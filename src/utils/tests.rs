#![cfg(test)]
use super::{defaults::{set, Set}, set_utils::{powerset, get_one}};

#[test]
fn test_set() {
    assert_eq!(set![1, 2, 3], Set::from([1, 2, 3]));
    let s: Set<i32> = Set::new();
    assert_eq!(set![], s);
}

#[test]
fn test_powerset() {
    let s = set!(2, 3, 5);
    let answers = powerset(&s);
    let mut ans_prods = set!();
    for ans in answers {
        let mut x = 1;
        for elem in ans {
            x *= elem;
        }
        ans_prods.insert(x);
    }
    assert_eq!(ans_prods, set!(1, 2, 3, 5, 6, 10, 15, 30));
}

#[test]
fn test_powerset_edge () {
    let empty: Set<i32> = set!();
    assert_eq!(powerset(&empty), vec!(set!()));

    let one = set!(1);
    assert!(powerset(&one).contains(&empty));
    assert!(powerset(&one).contains(&one));
    assert_eq!(powerset(&one).len(), 2)
}

#[test]
fn test_get_one() {
    assert_eq!(get_one(&set![]), None);
    assert!(set![1, 2, 3].contains(&get_one(&set![1, 2, 3]).expect("get_one did not return")));
}