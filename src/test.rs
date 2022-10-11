#![cfg(test)]

#[test]
fn foo() {
    let a = String::from("a");
    let b = String::from("a");
    assert_eq!(a, b);
}