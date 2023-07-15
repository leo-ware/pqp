import pandas as pd
import numpy as np

from pqp.utils import attrdict
from pqp.symbols.variable import Variable
from pqp.data.domain import make_domain, Domain, CategoricalDomain
from pqp.utils.exceptions import InferredDomainWarning, UnitDomainWarning
from pqp.refutation import Result, Operation, Step

class Data(Result):
    def __init__(self, df, vars=None, validate_domain=True, **kwargs):
        """Class representing datasets, wraps a pandas DataFrame and contains some metadata

        The main job of this class is to validate/create a set of symbolic variables that 
        align with the columns names on `df`.

        Examples:

        >> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        >> # it can infer a discrete domain for the variables
        >> Data(df, vars=[Variable("x"), Variable("y")])
        >> Data(df, vars={"x": Variable("X"), "y": Variable("Y")}) # capitalizes names

        >> # or you can specify the domain explicitly
        >> Data(df, vars={"x": DiscreteDomain([1, 2, 3, 4, 6]), "y": ContinuousDomain([1, 10])})
        >> Data(df, vars={"x": "discrete", "y": "continuous"})
        >> Data(df, vars={"x": None, "y": None}) # specifies an unknown domain

        >> # examples of invalid calls
        >> Data(df, vars={"x": Variable("x"), "z": Variable("z")}) # z not in df
        >> Data(df, vars={"x": Variable("x"), "y": "some name"}) # "some name" is interpreted as a domain type


        Args:
            df (pandas.DataFrame): the dataset
            vars (list or dict): the variables in the dataset, either a list of `Variable` (names
                must match columns in `df`) or a `dict` mapping column names in `df` to `Variable` 
                or str specifying the type of the variable's domain
            validate_domain (bool): if False, do not validate that the data conforms to the domains 
                specified, defaults to True
            silence_inferred_domain_warning (bool): if True, silences the default warning when
                the domain of a variable is inferred
            silence_unit_domain_warning (bool): if True, silences the default warning when an inferred
                domain for a variable has only a single possible value
        
        Attributes:
            df (pandas.DataFrame): the dataset
            vars (dict): a dict mapping variable names to `Variable` objects
        """
        self.step = Step("Data Processing")
        self.operation = Operation(self.__init__, [df], {"vars": vars, "validate_domain": validate_domain, **kwargs})

        self._silence_inferred_domain_warning = kwargs.get("silence_inferred_domain_warning", True)
        self._silence_unit_domain_warning = kwargs.get("silence_unit_domain_warning", False)

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"df must be a pandas DataFrame, not {type(self.df)}")
        
        self.df = df

        if vars is None:
            vars = [Variable(name, domain=self._make_domain(name, 'infer', self.df[name])) for name in list(self.df.columns)]

        self.vars = self._interpret_vars_arg(vars)
        self._confirm_vars_match_df_cols()
        self._confirm_vars_have_domains()
        self._record_assumptions()

        if validate_domain:
            self._validate_domain()

    def _make_domain(self, name, domain_type, values=None):
        if not self._silence_inferred_domain_warning:
            raise InferredDomainWarning(f'Inferred domain for variable "{name}"')
        domain = make_domain(domain_type, values)
        if (domain.get_cardinality() <= 1) and not self._silence_unit_domain_warning:
            raise UnitDomainWarning(f'Domain for variable "{name}" has cardinality <= {domain.get_cardinality()}')
        return domain
    
    def _interpret_vars_arg(self, vars):
        # this is gonna take in whatever terrible argument form the user used and
        # return an attrdict mapping column names to Variable objects
        if isinstance(vars, dict):
            var_index = vars
            for name, var in vars.items():
                if isinstance(var, str):
                    if name not in self.df.columns:
                        raise ValueError(f'"{name}" not found in DataFrame columns')
                    domain = self._make_domain(name, var, values=self.df[name])
                    var_index[name] = Variable(name, domain=domain)
                elif isinstance(var, Domain):
                    var_index[name] = Variable(name, domain=var)
                elif not isinstance(var, Variable):
                    raise TypeError(f"expected Variable, Domain, or str, but encountered type {type(var)}")
        else:
            try:
                vars = list(vars)
            except Error:
                raise TypeError(f"cannot interpret vars of type {type(var)}")
            
            var_index = {}
            for var in vars:
                if isinstance(var, Variable):
                    if var.domain == None:
                        if var.name not in self.df.columns:
                            raise ValueError(f'Variable "{var.name}" not found in DataFrame columns')
                        var.domain = self._make_domain(var.name, "infer", values=self.df[var.name])
                else:
                    raise TypeError(f"vars must be a list of Variables, found element of type {type(var)}")
                var_index[var.name] = var
        
        return attrdict(var_index)
    
    def _record_assumptions(self):
        for name, var in self.vars.items():
            self.step.assume(f"{name} is on {var.domain}")
    
    def _confirm_vars_match_df_cols(self):
        # confirm every variable in self.vars has a corresponding column in self.df
        cols = set(self.df.columns)
        for name, var in self.vars.items():
            if name not in cols:
                raise ValueError(f'Variable "{var}" not found in DataFrame columns')
            cols.remove(name)

        # for every column we dont have a variable for, infer one
        for name in cols:
            domain = self._make_domain(name, "infer", values=self.df[name])
            self.vars[name] = Variable(name, domain=domain)
    
    def _confirm_vars_have_domains(self):
        for name, var in self.vars.items():
            if var.domain == None:
                var.domain = self._make_domain(name, "infer", values=self.df[name])
    
    def _validate_domain(self):
        for name, var in self.vars.items():
            if var.domain == None:
                raise ValueError(f'Variable "{var}" has no domain')
            var.domain.validate_or_throw(self.df[name])
    
    @property
    def n(self):
        return self.df.shape[0]
    
    def domain_of(self, var):
        if isinstance(var, Variable):
            var = var.name
        try:
            return self.vars[var].domain
        except KeyError:
            raise ValueError(f'{repr(var)} not found in vars')
    
    def _domains(self):
        return {var: var.domain for var in self.vars.values()}
    
    def quantize(self, var, n_bins=2):
        step = self.step.substep(f'Quantizing {var} into {n_bins} bins')
        if isinstance(var, Variable):
            var = var.name        
        quantized = pd.cut(self.df[var], n_bins)
        for el in np.unique(quantized):
            step.write(f"Mapping elements on ({el.left}, {el.right}] to {el.mid}")
        self.df[var] = np.array([i.mid for i in quantized])
        self.vars[var] = Variable(var, domain=CategoricalDomain(self.df[var]))
