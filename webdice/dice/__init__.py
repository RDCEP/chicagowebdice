from __future__ import division
import json
import numpy as np
from params import DiceParams, Dice2010Params, DiceUserParams, DiceDataMatrix
from equations.loop import Loop
from equations_ne.loop import LoopOpt


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
        self.vars = self.params.vars
        self.scc = self.params.scc
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
        u_p = DiceUserParams()
        return [k for k, v in u_p.__dict__.iteritems() if k[0] != '_']

    @property
    def model_vars(self):
        """
        List of model variables to be included with output to graphs and CSV.
        """
        return [k for k, v in self.vars.__dict__.iteritems() if k[0] != '_']

    @property
    def welfare(self):
        """
        Objective function
        ...
        Returns
        -------
        float
        """
        return np.sum(self.vars.utility_discounted)

    def step(self, i, df, miu=None, deriv=False, opt=False, emissions_shock=0.0):
        """
        Single step for calculating endogenous variables
        ...
        Args
        ----
        i : int, index of current step
        df : object, DiceDataMatrix
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
        pd.DataFrame : self.vars
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
            self.step(i, self.vars, _miu, deriv=deriv, opt=opt)
        if scc:
            self.get_scc(_miu)
        return self.vars

    def set_opt_values(self, df):
        gf = (
            df.utility_discounted[:, :60].sum(axis=0) -
            df.utility_discounted[:, 60].sum()
        ) * self.opt_scale / self.eps
        self.opt_grad_f = gf
        self.opt_obj = (
            df.utility_discounted[:, 60].sum() * self.opt_scale)

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
        df = DiceDataMatrix(np.tile(self.vars, (61, 1, 1)).transpose(1, 2, 0))
        for i in xrange(self.params.tmax):
            df.miu[i, :] = miu[i]
            df.miu[i, i] += self.eps
            self.step(i, df, df.miu[i], deriv=True, opt=True)
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
        df = DiceDataMatrix(np.tile(self.vars, (61, 1, 1)).transpose(1, 2, 0))
        for i in xrange(self.params.tmax):
            df.miu[i, :] = miu[i]
            df.miu[i, i] += self.eps
            self.step(i, df, df.miu[i], deriv=True, opt=True)
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
        for i in xrange(20):
            th = self.params.scc_horizon
            future = th - i
            self.scc[:] = self.vars[:]
            for j in range(i, th + 1):
                shock = 0
                if j == i:
                    shock = 1.0
                self.step(j, self.scc, miu=miu, emissions_shock=shock)
            diff = (
                self.vars.consumption_pc[i:th] -
                self.scc.consumption_pc[i:th]
            ).clip(0) * self.scc.consumption_discount[:future]
            self.vars.scc[i] = np.sum(diff) * 1000 * 10 * (12 / 44)

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
            print('OPTIMIZATION ERROR: It appears that you do not have '
                  'pyipopt installed. Please install it before running '
                  'optimization.')
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
            if (_x0 == self.opt_x).all() and self.opt_obj is not None:
                return self.opt_obj
            else:
                self.opt_x = _x0.copy()
                return self.obj_loop(_x0)
        def eval_grad_f(_x0):
            if (_x0 == self.opt_x).all() and self.opt_grad_f is not None:
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
        # nlp.str_option('derivative_test', 'first-order')
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
        output = dict(parameters=None, data=None)
        output['parameters'] = {p: getattr(self.params, p) for p in self.user_params if type(p) in ['float', 'integer']}
        output['data'] = {p: list(getattr(self.vars, p)) for p in self.vars}
        return json.dumps(output)


class Dice2010(Dice):
    def __init__(self, optimize=False):
        super(Dice2010, self).__init__()
        self.params = Dice2010Params()
        self.vars = self.params.vars
        self.dice_version = 2010
        self.opt_tol = 1e-5


class Dice2007(Dice):
    def __init__(self, optimize=False):
        super(Dice2007, self).__init__()
        self.dice_version = 2007
        self.opt_tol = 1e-5


if __name__ == '__main__':
    run_scenario = 1
    if run_scenario:
        d = Dice2007()
        d.params.elasmu = 2
        d.params.prstp = .01
        d.params.carbon_model = 'beam_carbon'
        d.params.damages_model = 'productivity_fraction'
        d.params.prod_frac = .1
        d.loop(opt=0)
        print d.vars.scc[:2].mean()