#![cfg(test)]
use super::defaults::{set, Set};

#[test]
fn test_set() {
    assert_eq!(set![1, 2, 3], Set::from([1, 2, 3]));
    let s: Set<i32> = Set::new();
    assert_eq!(set![], s);
}