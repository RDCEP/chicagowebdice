from __future__ import division
import numpy as np
import pyipopt
from params import Dice2007Params
from equations.loop import Loop

class Dice2007():
    """Variables, parameters, and step function for DICE 2007.
    ...
    Args
    ----
    optimize : boolean
    ...
    Attributes
    ----------
    eq : object
        webdice.equations.loop.Loop object
    ...
    Properties
    ----------
    parameters : list
        Names of all parameters to DICE
    vars : list
        Names of all DICE variables
    ...
    Methods
    -------
    loop()
        Initiate step() loop, get_ipopt_mu(), and scc()
    step()
        Step function for calculating endogenous variables
    get_scc()
        Call loop() to run calculations for SCC
    get_ipopt_mu()
        Interface with pyipopt to optimize miu
    format_output()
        Output text for Google Visualizer graph functions
    """
    def __init__(self, optimize=False):
        self.params = Dice2007Params()
        self.data = self.params._data
        self.eq = Loop(self.params)
        self.params._optimize = optimize
        self.eps = self.params._eps

    @property
    def user_params(self):
        """
        List of model parameters to be included with output to graphs and CSV.
        """
        return [k for k, v in self.params.__dict__.iteritems() if k[0] != '_']

    @property
    def vars(self):
        """
        List of model variables to be included with output to graphs and CSV.
        """
        return self.data.vars.columns.tolist()

    @property
    def welfare(self):
        """
        Objective function
        ...
        Returns
        -------
        float
        """
        return np.sum(self.data.vars.utility_discounted)

    def step(self, i, D, miu=None, deriv=False, f0=0.0, emissions_shock=0.0):
        """
        Single step for calculating endogenous variables
        ...
        Args
        ----
        i : int, index of current step
        D : object, pandas DataFrame of variables
        ...
        Kwargs
        ------
        miu : array, values for miu
        deriv : boolean
        f0 : float
        emissions_shock : float
        ...
        Returns
        -------
        pandas.DataFrame : 60 steps of all variables in D
        """
        (D.carbon_intensity[i], D.productivity[i], D.capital[i],
         D.backstop_growth[i], D.gross_output[i]
        ) = self.eq.productivity_model.get_model_values(i, D)
        if i > 0:
            D.productivity[i] *= self.eq.damages_model.get_production_factor(
                D.temp_atmosphere[i - 1]
            ) ** 10
        (D.miu[i], D.emissions_ind[i], D.emissions_total[i],
         D.carbon_emitted[i], D.tax_rate[i]
        ) = self.eq.emissions_model.get_emissions_values(i, D, deriv, miu)
        D.emissions_total[i] += emissions_shock
        D.mass_atmosphere[i], D.mass_upper[i], D.mass_lower[i] = (
            self.eq.carbon_model.get_model_values(i, D)
        )
        D.forcing[i] = self.eq.carbon_model.forcing(i, D)
        D.temp_atmosphere[i], D.temp_lower[i] = (
            self.eq.temperature_model.get_model_values(i, D)
        )
        D.abatement[i], D.damages[i], D.output[i], D.output_abate[i] = (
            self.eq.damages_model.get_model_values(i, D)
        )
        (D.consumption[i], D.consumption_pc[i], D.consumption_discount[i],
         D.investment[i]) = self.eq.consumption_model.get_model_values(i, D)
        D.utility[i], D.utility_discounted[i] = (
            self.eq.utility_model.get_model_values(i, D)
        )
        if deriv:
            self.params._derivative.fprime[i] = (
                (D.utility_discounted[i] - f0) / self.eps
            )
            D.miu = self.data.vars.miu
        return D

    def loop(self, miu=None, deriv=False, scc=True):
        """
        Loop through step function for calculating endogenous variables
        ...
        Kwargs
        ------
        miu : array
        deriv : boolean
        scc : boolean
        ...
        Returns
        -------
        pd.DataFrame : self.data.vars
        """
        self.eq.set_models(self.params)
        if self.params._optimize and miu is None:
            self.data.vars.miu = self.get_ipopt_mu()
            self.data.vars.miu[0] = self.params._miu_2005
        for i in range(self.params._tmax):
            self.step(i, self.data.vars, miu)
            if self.params._optimize and deriv:
                f0 = np.atleast_1d(self.data.vars.utility_discounted[i])
                self.step(
                    i, self.data.deriv, miu=miu, deriv=True, f0=f0
                )
        if scc:
            self.get_scc(miu)
        if self.params._optimize and miu is not None:
            if deriv:
                return self.params._derivative.fprime.transpose()
            else:
                return self.welfare
        return self.data.vars

    def get_scc(self, miu):
        """
        Calculate social cost of carbon
        ...
        Args
        ----
        miu : array, 60 values of miu
        ...
        Returns
        -------
        None
        ...
        Internal Variables
        ------------------
        x_range : integer, number of periods in output graph
        future_indices : integer, number of periods to
            calculate future consumption
        final_year : integer, last period of to calculate consumption
        shock : float, amount to 'shock' the emissions of the current period
        """
        x_range = 20
        for i in range(x_range):
            final_year = 29
            future_indices = final_year - i
            self.data.scc = self.data.vars.copy()
            for j in range(i, final_year):
                shock = 0
                if j == i:
                    shock = 1.0
                self.step(j, self.data.scc, miu=miu, emissions_shock=shock)
            DIFF = (
                (
                    self.data.vars.consumption_pc[i:final_year].values -
                    self.data.scc.consumption_pc[i:final_year].values
                ).clip(0) *
                self.data.scc.consumption_discount[:future_indices].values
            )
            self.data.vars.scc[i] = np.sum(DIFF) * 1000 * 10 * (12 / 44)

    def get_ipopt_mu(self):
        """
        Calculate optimal miu
        ...
        Args
        ----
        None
        ...
        Returns
        -------
        array : optimal miu
        ...
        Internal Variables
        ------------------
        x0 : array, initial guess
        M : integer, size of constraints
        nnzj : integer, number of non-zero values in Jacobian
        nnzh : integer, number of non-zero values in Hessian
        xl : array, lower bounds of objective
        xu : array, upper bounds of objective
        gl : array, lower bounds of constraints
        gu : array, upper bounds of constraints
        """
        x0 = np.ones(self.params._tmax)
        M = 0
        nnzj = 0
        nnzh = 0
        xl = np.zeros(self.params._tmax)
        xu = np.ones(self.params._tmax)
        gl = np.zeros(M)
        gu = np.ones(M) * 4.0
        def eval_f(x):
            return self.loop(x, scc=False)
        def eval_grad_f(x):
            return self.loop(x, deriv=True, scc=False)
        def eval_g(x):
            return np.zeros(M)
        def eval_jac_g(x, flag):
            if flag:
                return [], []
            else:
                return np.empty(M)
        r = pyipopt.create(
            self.params._tmax, xl, xu, M, gl, gu, nnzj, nnzh, eval_f,
            eval_grad_f, eval_g, eval_jac_g
        )
        x, zl, zu, obj, status = r.solve(x0)
        return x

    def format_output(self):
        """
        Output text for Google Visualizer graph functions.
        ...
        Returns
        -------
        str
        """
        output = ['%s %s' % (
            p, getattr(self.params, p)) for p in self.user_params]
        output += ['%s %s' % (
            p, ' '.join(map(str, list(getattr(self.data.vars, p))))
        ) for p in self.vars ]
        return '\n'.join(output)


if __name__ == '__main__':
    pass