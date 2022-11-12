use super::Form;

/*
- promote hedges to top level: form -> hedge
- remove empty marginals: marginal -> form
- cancel marginal terms with joint terms: marginal(p) -> marginal(p)
- remove empty ps from products: product -> product | one
- eliminate quotients with unit denominators: quotient -> form
- merge nested sums: marginal(marginal) -> marginal
- remove constant factors from sums: marginal(product) -> product(expr, marginal(product))
- cancel identical terms in quotient: quotient -> quotient
    - more complex variations on this
- merge adjacent products, quotients: product(product | quotient) -> product | quotient
- convert quotients to conditional probabilities (???)
*/

fn promote_hedges (f: Form) -> Form {
    if f.contains_hedge() {
        Form::Hedge
    } else {
        f
    }
}

fn remove_empty_marginal (f: Form::Marginal) -> Form {
    let Form::Marginal(over, expr) = f;
    if over.empty() {
        expr
    } else {
        f
    }
}

fn cancel_marginal_joint_terms (f: Form::Marginal) -> Form {
    let Form::Marginal(over, summand) = f;
    if let Form::P(vars, given) = summand {
        if given.empty() && !intersection(&over, &vars).empty() {
            return Form::Marginal(difference(&over, &vars), Form::P(difference(&vars, &over), given));
        }
    }
    return f;
}

