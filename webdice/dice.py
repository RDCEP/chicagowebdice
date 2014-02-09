from __future__ import division
import numpy as np
import pandas as pd
from params import DiceParams, Dice2010Params
from equations.loop import Loop


class Dice(object):
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
        self.params = DiceParams()
        self.data = self.params._data
        self.eq = Loop(self.params)
        self.eps = self.params._eps
        self.dice_version = 2007
        self.opt_vars = 60
        self.opt_x = np.arange(self.opt_vars)
        self.opt_grad_f = None
        self.opt_obj = None
        self.opt_tol = 1e-4

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

    def step(self, i, D, miu=None, deriv=False, opt=False, emissions_shock=0.0):
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
        (
            D.carbon_intensity[i], D.productivity[i], D.capital[i],
            D.backstop_growth[i], D.gross_output[i]
        ) = self.eq.productivity_model.get_model_values(i, D)
        if i > 0:
            D.productivity[i] *= self.eq.damages_model.get_production_factor(
                D.temp_atmosphere[i - 1]
            ) ** 10
        (
            D.miu[i], D.emissions_ind[i],
            D.emissions_total[i], D.carbon_emitted[i],
            D.tax_rate[i]
        ) = self.eq.emissions_model.get_emissions_values(
            i, D, miu=miu, emissions_shock=emissions_shock, deriv=deriv, opt=opt
        )
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
        return D

    def loop(self, miu=None, deriv=False, scc=True, opt=False):
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
        D = self.data.vars
        self.eq.set_models(self.params)
        _miu = None
        if opt:
            print(1)
            if miu is not None:
                D = pd.Panel(
                    {i: self.data.vars for i in xrange(self.params._tmax + 1)}
                ).transpose(2, 0, 1)
            else:
                _miu = self.get_ipopt_mu()
                _miu[0] = self.params._miu_2005
        for i in range(self.params._tmax):
            if opt and miu is not None:
                D.miu.ix[:][i] = miu[i]
                D.miu.ix[i][i] += self.eps
                _miu = D.miu[i]
            self.step(i, D, _miu, deriv=deriv, opt=opt)
        if scc:
            self.get_scc(_miu)
        if opt and miu is not None:
            self.opt_grad_f = ((
                D.utility_discounted.ix[:59,:].sum(axis=1) -
                D.utility_discounted.ix[60,:].sum(axis=1)) / self.eps)
            self.opt_obj = D.utility_discounted.ix[60,:].sum(axis=1)
            if deriv:
                return self.opt_grad_f
            return self.opt_obj
        return D

    def obj_loop(self, miu):
        D = pd.Panel(
            {i: self.data.vars for i in xrange(self.params._tmax + 1)}
        ).transpose(2, 0, 1)
        for i in xrange(self.params._tmax):
            D.miu.ix[:][i] = miu[i]
            D.miu.ix[i][i] += self.eps
            _miu = D.miu[i]
            self.step(i, D, _miu, deriv=True, opt=True)
        self.opt_grad_f = ((
            D.utility_discounted.ix[:59,:].sum(axis=1) -
            D.utility_discounted.ix[60,:].sum(axis=1)) / self.eps)
        self.opt_obj = D.utility_discounted.ix[60,:].sum(axis=1)
        return self.opt_obj

    def grad_loop(self, miu):
        D = pd.Panel(
            {i: self.data.vars for i in xrange(self.params._tmax + 1)}
        ).transpose(2, 0, 1)
        for i in xrange(self.params._tmax):
            D.miu.ix[:][i] = miu[i]
            D.miu.ix[i][i] += self.eps
            _miu = D.miu[i]
            self.step(i, D, _miu, deriv=True, opt=True)
        self.opt_grad_f = ((
            D.utility_discounted.ix[:59,:].sum(axis=1) -
            D.utility_discounted.ix[60,:].sum(axis=1)) / self.eps)
        self.opt_obj = D.utility_discounted.ix[60,:].sum(axis=1) * -1e-5
        return self.opt_grad_f

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
        time_horizon : integer, last period of to calculate consumption
        shock : float, amount to 'shock' the emissions of the current period
        """
        x_range = 20
        for i in xrange(x_range):
            time_horizon = 59
            future_indices = time_horizon - i
            self.data.scc = self.data.vars.copy()
            for j in range(i, time_horizon):
                shock = 0
                if j == i:
                    shock = 1.0
                self.step(j, self.data.scc, miu=miu, emissions_shock=shock)
            DIFF = (
                (
                    self.data.vars.consumption_pc[i:time_horizon].values -
                    self.data.scc.consumption_pc[i:time_horizon].values
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
        try:
            import pyipopt
        except ImportError:
            print('OPTIMIZATION ERROR: It appears that you do not have pyipopt installed. Please install it before running optimization.')
        _n = 3
        x0 = np.concatenate((
            np.linspace(.5, 1, _n),
            np.ones(self.opt_vars - _n),
        ))
        x0 = np.ones(self.opt_vars)
        M = 0
        nnzj = 0
        nnzh = 0
        xl = np.zeros(self.params._tmax)
        xu = np.ones(self.params._tmax)
        gl = np.zeros(M)
        gu = np.ones(M) * 4.0
        def eval_f(_x0):
            if (_x0 == self.opt_x).all():
                return self.opt_obj
            else:
                self.opt_x = _x0.copy()
                return self.obj_loop(_x0)
        def eval_grad_f(_x0):
            if (_x0 == self.opt_x).all():
                return self.opt_grad_f.values
            else:
                self.opt_x = _x0.copy()
                return self.grad_loop(_x0)
        def eval_g(x):
            return np.zeros(M)
        def eval_jac_g(x, flag):
            if flag:
                return [], []
            else:
                return np.empty(M)
        pyipopt.set_loglevel(1)
        # nlp.num_option('tol', self.opt_tol)
        nlp = pyipopt.create(
            self.opt_vars, xl, xu, M, gl, gu, nnzj, nnzh, eval_f,
            eval_grad_f, eval_g, eval_jac_g,
        )
        nlp.num_option('tol', self.opt_tol)
        nlp.num_option('acceptable_tol', self.opt_tol * 5)
        nlp.int_option('acceptable_iter', 4)
        nlp.num_option('obj_scaling_factor', -1e-5)
        nlp.int_option('print_level', 5)
        nlp.str_option('linear_solver', 'ma27')
        # x, zl, zu, multiplier, obj, status = nlp.solve(x0)
        x = nlp.solve(x0)[0]
        nlp.close()
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


class Dice2010(Dice):
    def __init__(self, optimize=False):
        super(Dice2010, self).__init__()
        self.params = Dice2010Params()
        self.data = self.params._data
        self.dice_version = 2010
        self.opt_tol = 1e-6


class Dice2007(Dice):
    def __init__(self, optimize=False):
        super(Dice2007, self).__init__()
        self.dice_version = 2007
        self.opt_tol = 1e-6


if __name__ == '__main__':
    #pass
    profile = False
    d = Dice2007()
    d.params.carbon_model = 'beam_carbon'

    if profile:
        import cProfile

        cProfile.run('d.loop(opt=True)', 'dice_stats')
        import pstats
        p = pstats.Stats('dice_stats')
    else:
        d.loop()
        print(d.data.vars.mass_upper[:5])
        print(d.data.vars.mass_upper[-5:-1])
        print(d.data.vars.mass_lower[-5:-1])