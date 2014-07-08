from __future__ import division
import numpy as np
import numexpr as ne
import pandas as pd
from params import DiceParams, Dice2010Params
from equations.loop import Loop
from equations_ne.loop import LoopOpt
import __builtin__

try:
    __builtin__.profile
except AttributeError:
    def profile(func): return func
    __builtin__.profile = profile


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
        self.data = self.params.data
        self.eq = Loop(self.params)
        self.eps = 1e-8
        self.dice_version = 2007
        self.opt_vars = 60
        self.opt_x = np.arange(self.opt_vars)
        self.opt_grad_f = None
        self.opt_obj = None
        self.opt_tol = 1e-5
        self.opt_scale = 1e-4

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

    def step(self, i, df, miu=None, deriv=False, opt=False, emissions_shock=0.0):
        """
        Single step for calculating endogenous variables
        ...
        Args
        ----
        i : int, index of current step
        df : object, pandas DataFrame of variables
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
        pandas.DataFrame : 60 steps of all variables in df
        """
        (
            df.carbon_intensity[i], df.productivity[i], df.capital[i],
            df.backstop_growth[i], df.gross_output[i], df.intensity_decline[i],
            df.population[i],
        ) = self.eq.productivity_model.get_model_values(i, df)
        if i > 0:
            df.productivity[i] *= self.eq.damages_model.get_production_factor(
                df.temp_atmosphere[i - 1]
            ) ** 10
        (
            df.miu[i], df.emissions_ind[i],
            df.emissions_total[i], df.carbon_emitted[i],
            df.tax_rate[i]
        ) = self.eq.emissions_model.get_model_values(
            i, df, miu=miu, emissions_shock=emissions_shock, deriv=deriv, opt=opt
        )
        df.mass_atmosphere[i], df.mass_upper[i], df.mass_lower[i] = (
            self.eq.carbon_model.get_model_values(i, df)
        )
        df.forcing[i] = self.eq.carbon_model.forcing(i, df)
        df.temp_atmosphere[i], df.temp_lower[i] = (
            self.eq.temperature_model.get_model_values(i, df)
        )
        df.abatement[i], df.damages[i], df.output[i], df.output_abate[i] = (
            self.eq.damages_model.get_model_values(i, df)
        )
        (df.consumption[i], df.consumption_pc[i], df.consumption_discount[i],
         df.investment[i]) = self.eq.consumption_model.get_model_values(i, df)
        df.utility[i], df.utility_discounted[i] = (
            self.eq.utility_model.get_model_values(i, df)
        )
        return df

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
        _miu = None
        if opt:
            self.eq = LoopOpt(self.params)
            self.eq.set_models(self.params)
            _miu = self.get_ipopt_miu()
            _miu[0] = self.params.miu_2005
        self.eq = Loop(self.params)
        self.eq.set_models(self.params)
        for i in range(self.params.tmax):
            self.step(i, self.data.vars, _miu, deriv=deriv, opt=opt)
        if scc:
            self.get_scc(_miu)
        return self.data.vars

    def set_opt_values(self, df):
        self.opt_grad_f = (
            df.utility_discounted.ix[:59, :].sum(axis=1) -
            df.utility_discounted.ix[60, :].sum(axis=1)
        ) * self.opt_scale / self.eps
        self.opt_obj = (
            df.utility_discounted.ix[60, :].sum(axis=1) * self.opt_scale)

    def obj_loop(self, miu):
        """
        Calculate gradient of objective function using finite differences
        ...
        Args
        ----
        miu : array, 60 values of miu
        ...
        Returns
        -------
        float : value of objective (utility)
        ...
        """
        df = pd.Panel(
            {i: self.data.vars for i in xrange(self.params.tmax + 1)}
        ).transpose(2, 0, 1)
        for i in xrange(self.params.tmax):
            df.miu.ix[:][i] = miu[i]
            df.miu.ix[i][i] += self.eps
            _miu = df.miu[i]
            self.step(i, df, _miu, deriv=True, opt=True)
        self.set_opt_values(df)
        return self.opt_obj

    def grad_loop(self, miu):
        """
        Calculate gradient of objective function using finite differences
        ...
        Args
        ----
        miu : array, 60 values of miu
        ...
        Returns
        -------
        array : gradient of objective
        ...
        """
        df = pd.Panel(
            {i: self.data.vars for i in xrange(self.params.tmax + 1)}
        ).transpose(2, 0, 1)
        for i in xrange(self.params.tmax):
            df.miu.ix[:][i] = miu[i]
            df.miu.ix[i][i] += self.eps
            _miu = df.miu[i]
            self.step(i, df, _miu, deriv=True, opt=True)
        self.set_opt_values(df)
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
            th = self.params.scc_horizon
            future = th - i
            self.data.scc = self.data.vars.copy()
            for j in range(i, th + 1):
                shock = 0
                if j == i:
                    shock = 1.0
                self.step(j, self.data.scc, miu=miu, emissions_shock=shock)
            diff = (
                self.data.vars.consumption_pc[i:th].values -
                self.data.scc.consumption_pc[i:th].values
            ).clip(0) * self.data.scc.consumption_discount[:future].values
            self.data.vars.scc[i] = np.sum(diff) * 1000 * 10 * (12 / 44)

    def get_ipopt_miu(self):
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
        x0 = np.concatenate(
            (np.linspace(0, 1, 40) ** (1 - np.linspace(0, 1, 40)), np.ones(20))
        )
        M = 0
        nnzj = 0
        nnzh = 0
        xl = np.zeros(self.params.tmax)
        xu = np.ones(self.params.tmax)
        xl[0] = .005
        xu[0] = .005
        xl[-20:] = 1
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
                return self.opt_grad_f
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
        nlp = pyipopt.create(
            self.opt_vars, xl, xu, M, gl, gu, nnzj, nnzh, eval_f,
            eval_grad_f, eval_g, eval_jac_g,
        )
        nlp.num_option('constr_viol_tol', 8e-7)
        nlp.int_option('max_iter', 30)
        nlp.num_option('max_cpu_time', 60)
        nlp.num_option('tol', self.opt_tol)
        # nlp.num_option('acceptable_tol', 1e-4)
        # nlp.int_option('acceptable_iter', 4)
        nlp.num_option('obj_scaling_factor', -1e+0)
        nlp.int_option('print_level', 0)
        nlp.str_option('linear_solver', 'ma57')
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
        self.data = self.params.data
        self.dice_version = 2010
        self.opt_tol = 1e-5


class Dice2007(Dice):
    def __init__(self, optimize=False):
        super(Dice2007, self).__init__()
        self.dice_version = 2007
        self.opt_tol = 1e-5


if __name__ == '__main__':
    from datetime import datetime
    t0 = datetime.now()
    profile = False
    d = Dice2007()
    if profile:
        import cProfile
        cProfile.run('d.loop(opt=True)', 'dice_stats')
        import pstats
        p = pstats.Stats('dice_stats').sort_stats('cumtime')
        p.print_stats(20)
    else:
        # d.loop()
        # print(d.data.vars)
        d.params.savings = .22
        d.params.fosslim = 100000
        d.params.elasmu = 2
        d.params.prstp = .01
        d.params.damages_model = 'productivity_fraction'
        d.params.carbon_model = 'beam_carbon'
        d.params.prod_frac = .25
        # d.loop(opt=True)
        d.loop(opt=False)

        print(d.data.vars.scc[:2].mean())
        print(d.data.vars.consumption[55:])
        # print(d.data.vars.ix[i, :] - d.data.scc.ix[i, :])
    t1 = datetime.now()
    print t1 - t0
        # import timeit
        # t = timeit.Timer('d = Dice2007(); d.loop(opt=True)', 'from webdice import Dice2007')
        # print t.repeat(1, 2)