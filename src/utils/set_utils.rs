use::std::collections::HashSet as Set;
use::std::hash::Hash;

use crate::graph::Node;

pub fn make_set<'a, T: Hash + Eq>(elems: impl Iterator<Item=T>) -> Set<T> {
    let mut s = Set::new();
    elems.for_each(|e| {s.insert(e);});
    return s;
}

pub fn difference(a: &Set<Node>, b: &Set<Node>) -> Set<Node> {
    a.difference(b).map(|e| *e).collect()
}

pub fn union(a: &Set<Node>, b: &Set<Node>) -> Set<Node> {
    a.union(b).map(|e| *e).collect()
}

pub fn intersection(a: &Set<Node>, b: &Set<Node>) -> Set<Node> {
    a.intersection(b).map(|e| *e).collect()
}


// pub fn find_superset<T>(sets: HashSet<HashSet<T>>, s: HashSet<T>) -> HashSet<T> {
//     for superset in sets {
//         if s.is_subset(superset) {
//             return s;
//         }
//     }
//     None;
// }

// fn calculate_hash<T: Hash>(t: &T) -> u64 {
//     let mut s = DefaultHasher::new();
//     t.hash(&mut s);
//     s.finish()
// }