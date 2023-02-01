use super::wrapper::{ModelWrapper, IDResult};

pub fn id(d_edges: Vec<(String, String)>, b_edges: Vec<(String, String)>, y: Vec<String>, x: Vec<String>, z: Vec<String>) -> IDResult {
    let mut model_wrapper = ModelWrapper::new();

    for (from, to) in d_edges {
        model_wrapper.add_effect(&from, &to);
    }
    for (from, to) in b_edges {
        model_wrapper.add_confounding(&from, &to);
    }

    let foo = model_wrapper.id(
        y.iter().cloned().collect(),
        x.iter().cloned().collect(),
        z.iter().cloned().collect()
    );

    return foo;
}