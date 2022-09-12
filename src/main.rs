mod model;

fn main() {
    let model = model::Model::new(
        &[
            ("x", &["z"]),
            ("y", &["x", "z"]),
        ],
        &[]
    );
    // println!("{:#?}", model);
    // println!("ancestors of y {:#?}", model.ancestors("y"));
    // println!("ancestors of z {:#?}", model.ancestors("z"));

    println!("{:#?}", model.topological_sort());
}
