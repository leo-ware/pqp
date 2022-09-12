use std::collections::HashSet;

mod model;

fn main() {
    let model = model::model::Model::new(
        &[
            ("x", &["z"]),
            ("y", &["x", "z"]),
        ],
        &[]
    );
    // println!("{:#?}", model);
    // println!("ancestors of y {:#?}", model.ancestors("y"));
    // println!("ancestors of z {:#?}", model.ancestors("z"));

    println!("{:#?}", model.subgraph(HashSet::from(["y", "x"])));
}
