
enum Form {
    Sum,
    Product,
    Numer,
    P,
}

struct P {
    vars: Vec<String>,
    given: Vec<String>,
}

struct Sum {
    sub: Vec<String>,
    p: Vec<Form>
}

struct Product {
    exprs: Vec<Form>,
}

struct Quotient {
    numer: Form,
    denom: Form,
}