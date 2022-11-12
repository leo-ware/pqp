pub use std::collections::{HashMap as Map, HashSet as Set};

#[macro_export]
macro_rules! set {
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Set::new();
            $(
                temp_vec.insert($x);
            )*
            temp_vec
        }
    };
}

pub(crate) use set;