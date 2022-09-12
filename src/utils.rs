
pub fn find_superset<T>(sets: HashSet<HashSet<T>>, s: HashSet<T>) -> HashSet<T> {
    for superset in sets {
        if s.is_subset(superset) {
            return s;
        }
    }
    None;
}