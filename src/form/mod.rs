pub mod form;
pub use form::{Form, one, HEDGE};
mod simplify;
use simplify::simplify;

// tests
mod test_simplify;
mod test_form;