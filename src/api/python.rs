use pyo3::prelude::*;
use rand::Rng;
use std::cmp::Ordering;
use std::io;

use super::functions;
use super::wrapper::IDResult;

#[pyfunction]
fn hello_world () {
    println! ( "Hello, world!" );
}

#[pyfunction]
fn id (d_edges: Vec<(String, String)>, b_edges: Vec<(String, String)>, x: Vec<String>, y: Vec<String>, z: Vec<String>) -> PyResult<String> {
    println!("hi im rust");
    println!("d_edges: {:?}", d_edges);
    println!("b_edges: {:?}", b_edges);
    println!("x: {:?}", x);
    println!("y: {:?}", y);
    println!("z: {:?}", z);
    
    let result = functions::id(d_edges, b_edges, x, y, z).estimand_json.replace("\\", "");
    Ok(result)
}

#[pymodule]
pub fn pqp_backend(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_world, m)?)?;
    m.add_function(wrap_pyfunction!(id, m)?)?;
    Ok(())
}