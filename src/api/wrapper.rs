use itertools::Itertools;

use crate::{
    model::{Model, ModelBuilder},
    utils::defaults::{set, Set, Map},
    graph::Node,
    form::{Form, form::AbstractForm},
};

pub struct ModelWrapper {
    model_builder: ModelBuilder,
    vars: Map<String, Node>,
}

pub type FormWrapper = AbstractForm<String>;

impl FormWrapper {
    pub fn to_json(&self) -> String {
        match self {
            FormWrapper::Marginal(sub, exp) => {
                let sub_vec: Vec<String> = sub.iter().cloned().collect();
                format!(
                    "{{\"type\": \"Marginal\", \"sub\": [{:?}], \"exp\": {}}}",
                    sub_vec.iter().format_default(", "),
                    exp.to_json()
                )
            },
            FormWrapper::Quotient(numer, denom) => {
                format!(
                    "{{\"type\": \"Quotient\", \"numer\": {}, \"denom\": {}}}",
                    numer.to_json(),
                    denom.to_json()
                )
            },
            FormWrapper::P(vars, given) => {
                format!(
                    "{{\"type\": \"P\", \"vars\": [{:?}], \"given\": [{:?}]}}",
                    vars.iter().format_default(", "),
                    given.iter().format_default(", ")
                )
            },
            FormWrapper::Product(exprs) => {
                format!(
                    "{{\"type\": \"Product\", \"exprs\": [{}]}}",
                    exprs.iter().map(|e| {e.to_json()}).format_default(", ")
                )
            },
            FormWrapper::Hedge => "{\"type\": \"Hedge\"}".to_string(),
        }.replace("\\", "")
    }
}

impl ModelWrapper {
    pub fn new() -> ModelWrapper {
        ModelWrapper {
            model_builder: ModelBuilder::new(),
            vars: Map::new(),
        }
    }

    fn get_or_add_var(&mut self, name: &str) -> Node {
        if self.vars.contains_key(name) {
            return self.vars[name];
        } else {
            let var = self.vars.len() as i32;
            self.vars.insert(name.to_string(), var);
            self.model_builder.add_node(var);
            return var;
        }
    }

    pub fn form_sub(&self, form: Form) -> FormWrapper {
        let reversed: Map<i32, String> = self.vars.iter()
            .map(|(k, v)| (*v, k.clone()))
            .collect();

        fn substitute(f: &Form, reversed: &Map<i32, String>) -> FormWrapper {
            match f {
                Form::Marginal(sub, exp) => {
                    let sub: Set<String> = sub.iter().map(|s| reversed[s].to_owned()).collect();
                    let exp = substitute(exp, reversed);
                    FormWrapper::Marginal(sub, Box::new(exp))
                },
                Form::Quotient(numer, denom) => {
                    let numer = substitute(numer, reversed);
                    let denom = substitute(denom, reversed);
                    FormWrapper::Quotient(Box::new(numer), Box::new(denom))
                },
                Form::P(vars, given) => {
                    let vars = vars.iter().map(|s| reversed[s].to_owned()).collect();
                    let given = given.iter().map(|s| reversed[s].to_owned()).collect();
                    FormWrapper::P(vars, given)
                },
                Form::Product(exprs) => {
                    let exprs = exprs.iter().map(
                        |e| substitute(e, reversed)
                    ).collect();
                    FormWrapper::Product(exprs)
                },
                Form::Hedge => FormWrapper::Hedge,
            }
        }

        return substitute(&form, &reversed);
    }

    pub fn add_effect(&mut self, cause: &str, effect: &str) {
        let cause_n = self.get_or_add_var(cause);
        let effect_n = self.get_or_add_var(effect);
        // TODO: this seems backwards (!!??) but it works
        self.model_builder.add_directed_edge(effect_n, cause_n);
    }

    pub fn add_confounding(&mut self, cause: &str, effect: &str) {
        let cause_n = self.get_or_add_var(cause);
        let effect_n = self.get_or_add_var(effect);
        self.model_builder.add_confounded_edge(cause_n, effect_n);
    }

    pub fn id(&self, y: Set<String>, x: Set<String>, z: Set<String>) -> IDResult {

        let retrieve = |s: &String| {
            if self.vars.contains_key(s) {
                self.vars[s]
            } else {
                panic!("Variable {} not found in graph", s);
            }
        };

        let y_n: Set<Node> = y.iter().map(retrieve).collect();
        let x_n: Set<Node> = x.iter().map(retrieve).collect();
        let z_n: Set<Node> = z.iter().map(retrieve).collect();

        let model = ModelBuilder::to_model(Box::new(self.model_builder.to_owned())).cond(&z_n);
        let p = model.id(&y_n, &x_n);

        // string formatting of query
        let mut query = "P(".to_string();
        if !y.is_empty() {
            for each in y { query += &format!("{}, ", each); }
            query += "| ";
            for each in x { query += &format!("{}, ", each); }
            for each in z { query += &format!("do({}), ", each); }
            query.pop();
            query.pop();
            query += ")"
        }

        return IDResult {
            estimand_json: self.form_sub(p).to_json(),
            query_string: query,
        };
    }
}

#[derive(Debug)]
pub struct IDResult {
    pub estimand_json: String,
    pub query_string: String,
}