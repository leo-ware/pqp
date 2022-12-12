use::std::collections::HashSet as Set;
use::std::hash::Hash;

use crate::graph::Node;

pub fn copy_set <T: Eq + Hash + Copy>(s: &Set<T>) -> Set<T> {
    s.iter().map(|e| *e).collect()
}

// TODO: make this lazy
// TODO: return values sorted by size
// adapted from https://gist.github.com/synecdoche/9ade913c891dda6fcf1cdac823e7d524
pub fn powerset<T: Clone + Eq + Hash>(s: &Set<T>) -> Vec<Set<T>> {
    let elems: Vec<T> = s.iter().cloned().collect();
    let mut v: Vec<Set<T>> = Vec::new();

    for mask in 0..(1 << elems.len()) {
        let mut ss: Set<T> = Set::new();
        let mut bitset = mask;
        while bitset > 0 {
            // isolate the rightmost bit to select one item
            let rightmost: u64 = bitset & !(bitset - 1);
            // turn the isolated bit into an array index
            let idx = rightmost.trailing_zeros();
            let item = (*elems.get(idx as usize).unwrap()).clone();
            ss.insert(item);
            // zero the trailing bit
            bitset &= bitset - 1;
        }
        v.push(ss);
    }
    
    return v;
}

pub fn make_set<'a, T: Hash + Eq>(elems: impl Iterator<Item=T>) -> Set<T> {
    let mut s = Set::new();
    elems.for_each(|e| {s.insert(e);});
    return s;
}

pub fn get_one(a: &Set<Node>) -> Option<Node> {
    for node in a.iter() {
        return Some(*node);
    }
    None
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

// TODO: speed
pub fn symmetric_difference(a: &Set<Node>, b: &Set<Node>) -> Set<Node> {
    return difference(&union(a, b), &intersection(a, b));
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