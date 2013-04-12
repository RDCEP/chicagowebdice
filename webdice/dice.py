import numpy as np
import pyipopt
from params import Dice2007Params
import equations
from equations.damages import *

class Dice2007(Dice2007Params):
    """Variables, parameters, and step function for DICE 2007.
    ...
    Attributes
    ----------
    eq : object
        webdice.equations.<foo>.Loop object
    Also see webdice.params.diceParams

    Properties
    ----------
    parameters : list
        Names of all parameters to DICE
    vars : list
        Names of all DICE variables
    damages_terms : array
        Values for damages function
    population_growth: array
        Population growth factor
    population : array
        Labor or population
    productivity_growth : array
        Growth rate of productivity
    intensity_decline : array
        Rate of carbon decline
    backstop_growth : array
        Growth of cost factor
    emissions_deforest : array
        Emission from deforestation
    utility_discount : array
        Average utility discount rate
    emissions_cap : array
        Emissions caps for treaty
    participation : array
        Participation in treaty
    forcing_ghg : array
        Forcing for GHGs
    output_abate : array
        Abatement as a percentage of output
    user_tax_rate : array
        Array of user-determined annual tax rates

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
        self.eq = equations.default.Loop()
        Dice2007Params.__init__(self)
        self.p = Dice2007Params()
        self.optimize = False
        if optimize:
            self.optimize = True
        self.treaty = False
        self.carbon_tax = False

    @property
    def user_params(self):
        """
        List of model parameters to be included with output to graphs and CSV.
        """
        return [
            'temp_co2_doubling', 'damages_exponent', 'productivity_decline',
            'intensity_decline_rate', 'e2050', 'e2100', 'e2150',
            'p2050', 'p2100', 'p2150', 'popasym', 'depreciation',
            'savings', 'fosslim', 'abatement_exponent', 'backstop_decline',
            'backstop_ratio', 'elasmu', 'prstp',
        ]

    @property
    def vars(self):
        """
        List of model variables to be included with output to graphs and CSV.
        """
        return [
            'capital', 'gross_output', 'emissions_ind',
            'emissions_total', 'mass_atmosphere', 'mass_upper',
            'mass_lower', 'forcing', 'temp_atmosphere',
            'temp_lower', 'damages', 'abatement', 'output', 'output_abate',
            'investment', 'carbon_emitted', 'consumption',
            'consumption_pc', 'utility', 'utility_discounted',
            'productivity', 'backstop_growth', 'carbon_intensity', 'miu', 'backstop',
            'population', 'tax_rate', 'scc', 'consumption_discount',
        ]

    @property
    def damages_terms(self):
        """
        temp coefficient; pi_2, temp squared coefficient;
        epsilon, damages exponent
        ...
        Returns
        -------
        array
        """
        return np.array(
            [self._a1, self._damages_coefficient, self.damages_exponent]
        )

    @property
    def population_growth(self):
        """
        L_g, Population growth factor
        ...
        Returns
        -------
        array
        """
        return (
            (np.exp(self._population_growth * self.t0) - 1) / 
            (np.exp(self._population_growth * self.t0))
        )

    @property
    def population(self):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return self._population_2005 * (1 - self.population_growth) + \
               self.population_growth * self.popasym

    @property
    def productivity_growth(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array
        """
        return self._productivity_growth * np.exp(
            -(self.productivity_decline / 100.) * 10 * self.t0
        )

    @property
    def intensity_decline(self):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array
        """
        return (
            self._intensity_growth * np.exp(
                -(self.intensity_decline_rate / 100) * 10 *
                self.t0 - self._intensity_quadratic * 10 * (self.t0 ** 2)
            )
        )

    @property
    def emissions_deforest(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array
        """
        return self._emissions_deforest_2005 * (1 - .1) ** self.t0

    @property
    def utility_discount(self):
        """
        R, Average utility discount rate
        ...
        Returns
        -------
        array
        """
        return 1 / ((1 + self.prstp) ** (10 * self.t0))

    @property
    def emissions_cap(self):
        """
        Emissions caps from treaty inputs
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            np.ones(5),
            (np.ones(5) * (100. - self.e2050)) / 100.,
            (np.ones(5) * (100. - self.e2100)) / 100.,
            (np.ones(45) * (100. - self.e2150)) / 100.,
        ))

    @property
    def participation(self):
        """
        phi, Fraction of emissions in control regime
        ...
        Returns
        -------
        array
        """
        if not self.treaty:
            return np.concatenate((
                np.linspace(
                    self._participation_2005, self._participation_2005, 1
                ),
                self._participation_2205 + (
                    self._participation_2015 - self._participation_2205
                ) * np.exp(
                    -self._participation_decline * np.arange(23)
                ),
                np.linspace(
                    self._participation_2205, self._participation_2205, 36
                ),
            ))
        p = [self.p2050, self.p2050, self.p2100, self.p2150, self._pmax]
        return np.concatenate((
            (p[1] + (p[0] - p[1]) * np.exp(np.arange(5) * -.25)) / 100.,
            (p[2] + (p[1] - p[2]) * np.exp(np.arange(5) * -.25)) / 100.,
            (p[3] + (p[2] - p[3]) * np.exp(np.arange(5) * -.25)) / 100.,
            (p[4] + (p[3] - p[4]) * np.exp(np.arange(45) * -.25)) / 100.,
        ))

    @property
    def forcing_ghg(self):
        """
        F_EX, Exogenous forcing for other greenhouse gases
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            self._forcing_ghg_2000 + .1 * (
                self._forcing_ghg_2100 - self._forcing_ghg_2000
            ) * np.arange(11),
            self._forcing_ghg_2000 + (np.ones(49) * .36),
        ))

    @property
    def user_tax_rate(self):
        """
        Optional user-defined carbon tax
        ...
        Returns
        -------
        array
        """
        c = [0, self.c2050, self.c2100,
             self.c2150, self._cmax]
        return np.concatenate((
            c[0] + ((c[1] - c[0]) / 5 * np.arange(5)),
            c[1] + ((c[2] - c[1]) / 5 * np.arange(5)),
            c[2] + ((c[3] - c[2]) / 5 * np.arange(5)),
            c[3] + ((c[3] - c[2]) / 5 * np.arange(45)),
        ))

    @property
    def output_abate(self):
        """
        Abatement as a percentage of output
        ...
        Returns
        -------
        array
        """
        # return self.data.vars.backstop_growth * self.data.vars.miu ** \
        #        self.abatement_exponent
        return self.data.vars.abatement / self.data.vars.gross_output * 100

    @property
    def backstop(self):
        """
        Cost of replacing clean energy
        ...
        Returns
        -------
        array
        """
        return self._backstop_2005 * (
            (self.backstop_ratio - 1 + 
             np.exp(-self.backstop_decline * self.t0)) / self.backstop_ratio
        ) * (12.0 / 44.0)

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

    def step(self, i, D, miu=None, deriv=False, epsilon=1e-3, f0=0.0,
             emissions_shock=0.0, consumption_shock=0.0):
        """
        Single step for calculating endogenous variables
        ...
        Accepts
        -------
        i : int, index of current step
        D : object, pandas DataFrame of variables
        miu : array, values for miu
        deriv : boolean
        epsilon : float
        f0 : float
        emissions_shock : float
        consumption_shock : float
        ...
        Returns
        -------
        pandas.DataFrame : 60 steps of all variables in D
        """
        ii = i - 1
        if i > 0:
            D.carbon_intensity[i] = D.carbon_intensity[ii] / (
                1 - self.intensity_decline[i])
            D.productivity[i] = D.productivity[ii] / (
                1 - self.productivity_growth[ii])
            D.capital[i] = self.eq.capital(
                D.capital[ii], self.depreciation, D.investment[ii]
            )
            D.productivity[i] *= self.eq.get_production_factor(
                self.damages_terms, D.temp_atmosphere[ii]
            )
        D.backstop_growth[i] = (
            self.backstop[i] * D.carbon_intensity[i] / self.abatement_exponent
        )
        D.gross_output[i] = self.eq.gross_output(
            D.productivity[i], D.capital[i], self._output_elasticty,
            self.population[i]
        )
        if self.optimize:
            if miu is not None:
                if deriv:
                    D.miu = miu
                    D.miu[i] = D.miu[i] + epsilon
                else:
                    D.miu[i] = miu[i]
        else:
            if i > 0:
                if self.treaty:
                    D.miu[i] = self.eq.miu(
                        D.emissions_ind[ii], self.emissions_cap[ii],
                        D.emissions_ind[0],
                        D.carbon_intensity[i], D.gross_output[i]
                    )
                elif self.carbon_tax:
                    D.miu[i] = (
                        (self.user_tax_rate[i] / (self.backstop[i] * 1000)) **
                        (1 / (self.abatement_exponent - 1))
                    )
                else:
                    D.miu[i] = 0.
        D.tax_rate[i] = self.eq.tax_rate(
            self.backstop[i], D.miu[i], self.abatement_exponent
        )
        D.emissions_ind[i] = self.eq.emissions_ind(
            D.carbon_intensity[i], D.miu[i], D.gross_output[i]
        )
        D.emissions_total[i] = self.eq.emissions_total(
            D.emissions_ind[i], self.emissions_deforest[i]
        )
        D.emissions_total[i] += emissions_shock
        if i > 0:
            D.carbon_emitted[i] = (
                D.carbon_emitted[ii] + D.emissions_total[i] * 10
            )
        else:
            D.carbon_emitted[i] = 10 * D.emissions_total[i]
        if D.carbon_emitted[i] > self.fosslim:
            D.miu[i] = 1
            D.emissions_total[i] = 0
            D.carbon_emitted[i] = self.fosslim
        if i > 0:
            D.mass_atmosphere[i] = self.eq.mass_atmosphere(
                D.emissions_total[ii], D.mass_atmosphere[ii],
                D.mass_upper[ii], self.carbon_matrix
            )
            D.mass_upper[i] = self.eq.mass_upper(
                D.mass_atmosphere[ii], D.mass_upper[ii],
                D.mass_lower[ii], self.carbon_matrix
            )
            D.mass_lower[i] = self.eq.mass_lower(
                D.mass_upper[ii], D.mass_lower[ii], self.carbon_matrix
            )
        D.forcing[i] = self.eq.forcing(
            self._forcing_co2_doubling, D.mass_atmosphere[i], 
            self._mass_preindustrial, self.forcing_ghg[i]
        )
        if i > 0:
            D.temp_atmosphere[i] = self.eq.temp_atmosphere(
                D.temp_atmosphere[ii], D.temp_lower[ii], D.forcing[i], 
                self._forcing_co2_doubling, self.temp_co2_doubling,
                self.thermal_transfer
            )
            D.temp_lower[i] = self.eq.temp_lower(
                D.temp_atmosphere[ii], D.temp_lower[ii], self.thermal_transfer
            )
        D.abatement[i] = self.eq.abatement(
            D.gross_output[i], D.miu[i], D.backstop_growth[i],
            self.abatement_exponent, self.participation[i]
        )
        D.damages[i], D.output[i], D.consumption[i] = \
            self.eq.get_model_values(
                D.gross_output[i], D.temp_atmosphere[i],
                self.damages_terms, D.abatement[i], self.savings
            )
        D.consumption[i] += consumption_shock
        D.consumption_pc[i] = self.eq.consumption_pc(
            D.consumption[i], self.population[i]
        )
        if i > 0:
            D.consumption_discount[i] = self.eq.consumption_discount(
                self.prstp, self.population, self.elasmu, D.consumption_pc[0],
                D.consumption_pc[i], i
            )
        if i == 0:
            D.investment[i] = self.savings * self._output_2005
        else:
            D.investment[i] = self.eq.investment(
                self.savings, D.output[i]
            )
        D.utility[i] = self.eq.utility(
            D.consumption_pc[i], self.elasmu, self.population[i]
        )
        D.utility_discounted[i] = self.eq.utility_discounted(
            D.utility[i], self.utility_discount[i], self.population[i]
        )
        if deriv:
            self.derivative.fprime[i] = (D.utility_discounted[i] - f0) / epsilon
            D.miu = self.data.vars.miu
        return D

    def loop(self, miu=None, deriv=False, scc=True):
        """
        Loop through step function for calculating endogenous variables
        ...
        Accepts
        -------
        miu : array
        deriv : boolean
        scc : boolean
        ...
        Returns
        -------
        DataFrame : self.data.vars
        """
        if self.damages_model == 'exponential_map':
            self.eq = ExponentialMap(self.prod_frac)
        elif self.damages_model == 'tipping_point':
            self.eq = WeitzmanTippingPoint(self.prod_frac)
        elif self.damages_model == 'additive_output':
            self.eq = AdditiveDamages(self.prod_frac)
        elif self.damages_model == 'productivity_fraction':
            self.eq = ProductivityFraction(self.prod_frac)
        else:
            self.eq = DamagesModel(self.prod_frac)
        _epsilon = 1e-4
        if self.optimize and miu is None:
            self.data.vars.miu = self.get_ipopt_mu()
            self.data.vars.miu[0] = self._miu_2005
        for i in range(self.tmax):
            self.step(i, self.data.vars, miu)
            if self.optimize and deriv:
                f0 = np.atleast_1d(self.data.vars.utility_discounted[i])
                self.step(
                    i, self.data.deriv, miu=miu, epsilon=_epsilon,
                    deriv=True, f0=f0
                )
        if scc:
            self.get_scc(miu)
        if self.optimize and miu is not None:
            if deriv:
                return self.derivative.fprime.transpose()
            else:
                return self.data.vars.utility_discounted.sum()
        return self.data.vars

    def get_scc(self, miu):
        """
        Calculate social cost of carbon
        ...
        Accepts
        -------
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
            future_indices = self.tmax - x_range
            final_year = i + future_indices
            self.data['scc'] = self.data['vars'].copy()
            for j in range(i, final_year):
                shock = 0
                if j == i:
                    shock = 1.0
                self.step(j, self.data.scc, miu=miu, emissions_shock=shock)
            diff = 'consumption_pc'
            DIFF = np.absolute(
                self.data.vars[diff][i:final_year] -
                self.data.scc[diff][i:final_year]
            ).clip(0)
            self.data.vars.scc[i] = np.sum(
                DIFF *
                self.data.vars.consumption_discount[:future_indices].values
            ).clip(0) * 100000. * (12.0 / 44.0)

    def get_ipopt_mu(self):
        """
        Calculate optimal miu
        ...
        Accepts
        -------
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
        x0 = np.ones(self.tmax)
        M = 0
        nnzj = 0
        nnzh = 0
        xl = np.zeros(self.tmax)
        xu = np.ones(self.tmax)
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
            self.tmax, xl, xu, M, gl, gu, nnzj, nnzh, eval_f,
            eval_grad_f, eval_g, eval_jac_g
        )
        x, zl, zu, obj, status = r.solve(x0)
        return x

    def format_output(self):
        """Output text for Google Visualizer graph functions."""
        #TODO: This is sloppy as shit.
        output = ''
        for v in self.user_params:
            vv = getattr(self, v)
            output += '%s %s\n' % (v, vv)
        for v in self.vars:
            try:
                vv = getattr(self, v)
            except:
                vv = getattr(self.data['vars'], v)
            output += '%s %s\n' % (v, ' '.join(map(str, list(vv))))
        return output

def verify_out(d, param=None, value=None):
    if param is not None:
        x = getattr(d, param)
    d.loop()
    filename = '../verify/gams_%s_%s.csv' % (param, value)
    with open(filename, 'a') as f:
        _vars = [
            'miu', 'carbon_intensity', 'productivity', 'backstop_growth', 'capital',
            'output', 'mass_atmosphere', 'mass_upper', 'mass_lower', 
            'temp_atmosphere', 'temp_lower', 'investment', 'gross_output', 
            'forcing', 'emissions_ind', 'emissions_total', 'carbon_emitted',
            'participation', 'participation_markup', 'damages',
            'abatement', 'consumption', 'consumption_pc', 'utility',
            'utility_discounted', 'pref_fac',
            ]
        for i in range(d.tmax):
            for v in range(len(_vars)):
                if v + 1 == len(_vars):
                    t = '\n'
                else:
                    t = ','
                f.write(str(round(d.data['vars'][_vars[v]][i], 2)) + t)

if __name__ == '__main__':
    def run_verification():
        d = Dice2007()
        _params = [
            'temp_co2_doubling', 'damages_exponent', 'productivity_decline',
            'intensity_decline', 'abatement_exponent', 'backstop_decline',
            'backstop_ratio', 'popasym', 'depreciation', 'savings',
            'fosslim', 'elasmu', 'prstp',
        ]
        verify_out(d)
        for p in _params:
            verify_out(d, p, 'minimum')
            verify_out(d, p, 'maximum')

    d = Dice2007(optimize=True)
    # d.prstp = .015
    # d.damages_model = 'productivity_fraction'
    d.prod_frac = .2
    D = d.loop()
    print D.scc[:20]
