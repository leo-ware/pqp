
/// Remove duplicates from two sorted vectors simultaneously
/// Elements may appear more than once, in this case only the first occurence is removed
pub fn remove_duplicates_sorted<T: Ord + Eq + Clone>(v1: &Vec<T>, v2: &Vec<T>) -> (Vec<T>, Vec<T>) {
    let mut a = v1.to_owned();
    let mut b = v2.to_owned();

    let mut i = 0;
    let mut j = 0;
    while i < a.len() && j < b.len() {
        if a[i] == b[j] {
            a.remove(i);
            b.remove(j);
        } else if a[i] < b[j] {
            i += 1;
        } else {
            j += 1;
        }
    }

    return (a.to_vec(), b.to_vec());
}