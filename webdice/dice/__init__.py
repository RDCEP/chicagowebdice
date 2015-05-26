# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
from params import DiceParams, Dice2010Params, DiceUserParams, DiceDataMatrix
from equations.loop import Loop
from equations_ne.loop import LoopOpt


class Dice(object):
    """Dice object

    Variables, parameters, loop/step, and optimization functions
    for DICE objects.

    Args:
        None

    """
    def __init__(self):
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
        """List of parameters

        List of model parameters to be included with output to graphs and CSV.
        This list purposely leaves out model parameters whose names begin with
        an _, as they're assumed to be immutable.

        Args:
            None

        Returns:
            list: List of parameter names (strings)

        """
        u_p = DiceUserParams()
        return [k for k in u_p.__dict__.keys() if k[0] != '_']

    @property
    def model_vars(self):
        """Model variables

        List of model variables to be included with output to graphs and CSV.
        This list purposely leaves out model variables whose names begin with
        an _, though currently (Aug 2014) none exist.

        Args:
            None

        Returns:
            list: List of variable names as strings

        """
        return [k for k, v in self.vars.__dict__.iteritems() if k[0] != '_']

    @property
    def welfare(self):
        """Objective function: ∑(discounted utility)

        Args:
            None

        Returns:
            float: Value of objective function

        """
        return np.sum(self.vars.utility_discounted)

    def step(self, i, df, miu=None, deriv=False, opt=False,
             emissions_shock=0.0):
        """Step function

        Single step for calculating model variables at t. This is called from
        the loop() method.

        Args:
            i (int): index of current step
            df (DiceDataMatrix): numpy array of model variables

        Kwargs:
            miu (nd.array): values for miu
            deriv (bool): Whether or not to calculate a derivative
            opt (bool): Whether or not to optimize the scenario
            emissions_shock (float): Emissions shock for calculating SCC

        Returns:
            DiceDataMatrix: numpy array of model variables

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
            i, df, miu=miu, emissions_shock=emissions_shock, deriv=deriv,
            opt=opt
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
        (df.consumption[i], df.consumption_pc[i], df.discount_factor[i],
         df.discount_rate[i], df.discount_forward[i], df.investment[i]) = (
            self.eq.consumption_model.get_model_values(i, df))
        df.utility[i], df.utility_discounted[i] = (
            self.eq.utility_model.get_model_values(i, df)
        )
        return df

    def loop(self, miu=None, deriv=False, scc=True, opt=False):
        """Main loop

        Loop through step function for calculating endogenous variables. This
        method is called by hand, but also during derivative calculations
        when optimizing.

        Kwargs:
            miu (nd.array): values for miu
            deriv (bool): Whether or not to calculate a derivative
            scc (bool): Whether or not to calculate SCC
            opt (bool): Whether or not to optimize the scenario

        Returns:
            DiceDataMatrix: Array of model variables

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
        """Save current optimal values

        Save last gradient and last objective function. Speeds up optimization
        in the instance that miu (x) is unchanged form one iteration to the
        next.

        Args:
            df (DiceDataMatrix): Array of model variables

        Returns:
            None

        """
        gf = (
            df.utility_discounted[:, :60].sum(axis=0) -
            df.utility_discounted[:, 60].sum()
        ) * self.opt_scale / self.eps
        self.opt_grad_f = gf
        self.opt_obj = (
            df.utility_discounted[:, 60].sum() * self.opt_scale)

    def obj_loop(self, miu):
        """Objective function for optimization

        Calculate objective function. Is called by get_ipopt_miu().
        Calls loop(). Stores and returns result.

        Args:
            miu (nd.array): Array of values for miu, n = Dice().params.tmax

        Returns:
            float: value of objective (utility)

        """
        df = DiceDataMatrix(np.tile(self.vars, (61, 1, 1)).transpose(1, 2, 0))
        for i in xrange(self.params.tmax):
            df.miu[i, :] = miu[i]
            df.miu[i, i] += self.eps
            self.step(i, df, df.miu[i], deriv=True, opt=True)
        self.set_opt_values(df)
        return self.opt_obj

    def grad_loop(self, miu):
        """Gradient function for optimization

        Calculate gradient of objective function using finite differences.
        Is called by get_ipopt_miu(). Calls loop(). Stores and returns result.

        Args:
            miu (nd.array): Array of values for miu, n = Dice().params.tmax

        Returns:
            nd.array: gradient of objective

        """
        df = DiceDataMatrix(np.tile(self.vars, (61, 1, 1)).transpose(1, 2, 0))
        for i in xrange(self.params.tmax):
            df.miu[i, :] = miu[i]
            df.miu[i, i] += self.eps
            self.step(i, df, df.miu[i], deriv=True, opt=True)
        self.set_opt_values(df)
        return self.opt_grad_f

    def get_scc(self, miu):
        """Calculate SCC

        Calculate social cost of carbon. Called automatically from loop().

        Args:
            miu (nd.array): Array of values for miu, n = Dice().params.tmax

        Returns:
            None
        """
        for i in xrange(20):
            th = self.params.scc_horizon
            future = th - i
            # th = i + 40
            # future = 40
            self.scc[:] = self.vars[:]
            for j in range(i, th + 1):
                shock = 0
                if j == i:
                    shock = 1.0
                self.step(j, self.scc, miu=miu, emissions_shock=shock)
            diff = (
                self.vars.consumption_pc[i:th] -
                self.scc.consumption_pc[i:th]
            ).clip(0) * self.scc.discount_factor[:future]
            self.vars.scc[i] = np.sum(diff) * 1000 * 10 * (12 / 44)

    def get_ipopt_miu(self):
        """Optimized miu

        Calculate optimal miu. Called when opt=True is passed to loop().
        ...
        Args:
            None

        Returns
            nd.array: Array of optimal miu, n = params.tmax

        """
        try:
            import pyipopt
        except ImportError:
            pyipopt = None
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
        """Output as dict()

        Output model variables as dictionary.

        Args:
            None

        Returns:
            dict: Dictionary of model variables with lists of values

        """
        output = dict(parameters=None, data=None)
        output['parameters'] = {
            p: getattr(self.params, p) for p in self.user_params
            if type(getattr(self.params, p)) in [type(10), type(.10)]
        }
        output['data'] = {
            p: list(getattr(self.vars, p)) for p in self.model_vars
        }
        return output


class Dice2010(Dice):
    """Convenience object for DICE2010 scenarios.

    Example:
        d = Dice2010()
        d.loop(opt=False)
        print(d.vars)

    """
    def __init__(self):
        super(Dice2010, self).__init__()
        self.params = Dice2010Params()
        self.vars = self.params.vars
        self.dice_version = 2010
        self.opt_tol = 1e-5


class Dice2007(Dice):
    """Convenience object for DICE2007 scenarios.

    Example:
        d = Dice2007()
        d.params.elasmu = 2
        d.params.prstp = .01
        d.params.carbon_model = 'beam_carbon'
        d.params.damages_model = 'productivity_fraction'
        d.params.prod_frac = .1
        d.loop(opt=True)
        print(d.vars)

    """
    def __init__(self):
        super(Dice2007, self).__init__()
        self.dice_version = 2007
        self.opt_tol = 1e-5