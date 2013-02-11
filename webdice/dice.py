import numpy as np
import pyipopt
import pandas as pd
try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
except ImportError:
    pass
from params import Dice2007Params
import equations

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
    aa : array
    gfacpop: array
        Popula-ion growth factor
    l : array
        Labor or population
    ga : array
        Growth rate of productivity
    gsig : array
        Rate of carbon decline
    gcost1 : array
        Growth of cost factor
    etree : array
        Emission from deforestation
    rr : array
        Average utility discount rate
    ecap : array
        Emissions caps for treaty
    partfract : array
        Participation in treaty
    forcoth : array
        Forcing for GHGs

    Methods
    -------
    loop()
        Step function for calculating endogenous variables
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
        self.POW = 1.0

    @property
    def varscale(self):
        return {'mass_atmosphere': 1000., }

    @property
    def parameters(self):
        return [
            "elasmu", "prstp", "_pop0", "_gpop0", "popasym", "_a0",
            "_ga0", "dela", "dk", "_gama", "_q0", "_k0", "_sig0",
            "_gsigma", "dsig", "dsig2", "_eland0", "mat2000",
            "mu2000", "ml2000", "matPI", "t2xco2", "fex0", "fex1",
            "tocean0", "tatm0", "fco22x", "a1", "a2", "a3", "b11", "b12",
            "b21", "b22", "b23", "b32", "b33", "c1", "c2", "c3", "c4",
            "expcost2", "_pback", "backrat", "gback", "limmiu",
            "partfract1", "partfract2", "partfract21", "dpartfract",
            "e2050", "e2100", "e2150", "fosslim", "scale1", "scale2",
            "tmax", "numScen", "savings", "miu_2005", 'backstop',
        ]

    @property
    def user_params(self):
        return [
            't2xco2', 'a3', 'dela', 'dsig', 'e2050', 'e2100', 'e2150',
            'popasym', 'dk', 'savings', 'fosslim', 'expcost2', 'gback',
            'backrat', 'elasmu', 'prstp',
        ]

    @property
    def vars(self):
        return [
            'capital', 'gross_output', 'emissions_ind',
            'emissions_total', 'mass_atmosphere', 'mass_upper',
            'mass_lower', 'forcing', 'temp_atmosphere',
            'temp_lower', 'damage', 'abatement', 'output', 'output_abate',
            'investment', 'carbon_emitted', 'consumption',
            'consumption_pc', 'utility', 'utility_d',
            'al', 'gcost1', 'sigma', 'miu', 'backstop', 'l', 'tax_rate',
            'scc',
        ]

    @property
    def aa(self):
        """
        temp coefficient; pi_2, temp squared coefficient;
        epsilon, damage exponent
        ...
        Returns
        -------
        array : [a1, a2, a3]
        """
        return np.array([self.a1, self.a2, self.a3.value])

    @property
    def gfacpop(self):
        """
        L_g, Population growth factor
        ...
        Returns
        -------
        array : exp(gpop0 * t - 1) / exp(gpop * t)
        """
        return (np.exp(self._gpop0 * self.t0) - 1) / (np.exp(self._gpop0 *
                                                             self.t0))

    @property
    def l(self):
        """
        L, Population.
        ...
        Returns
        -------
        array : (exp(pop(0) * t) - 1) / exp(gpop(0) * t)
        """
        return self._pop0 * (1 - self.gfacpop) + self.gfacpop * \
            self.popasym.value

    @property
    def ga(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array : ga(0) * exp(-dela * 10 * t)
        """
        return self._ga0 * np.exp(-(self.dela.value / 100.) * 10 * self.t0)

    @property
    def gsig(self):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array : gsigma * exp(-dsig * 10 * t - disg2 * 10 * t^2)
        """
        return self._gsigma * np.exp(-(
            self.dsig.value / 100) * 10 * self.t0 - self.dsig2 * 10 *
            (self.t0 ** 2)
        )

    @property
    def backstop(self):
        """
        Backstop price
        ...
        Returns
        -------
        array : pback * ((backrat - 1 + exp(-gback * t)) / backrat
        """
        return self._pback * (
            (self.backrat.value - 1 + np.exp(-self.gback.value * self.t0)) /
            self.backrat.value)

    @property
    def etree(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array : Eland(0) * (1 - .1)^t
        """
        return self._eland0 * (1 - .1) ** self.t0

    @property
    def rr(self):
        """
        R, Average utility social discount rate
        ...
        Returns
        -------
        array : 1 / (1 + prstp)^t
        """
        return 1 / ((1 + self.prstp.value) ** (10 * self.t0))

    @property
    def ecap(self):
        """
        Emissions caps from treaty inputs
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            np.ones(5),
            (np.ones(5) * (100. - self.e2050.value)) / 100.,
            (np.ones(5) * (100. - self.e2100.value)) / 100.,
            (np.ones(45) * (100. - self.e2150.value)) / 100.,
        ))

    @property
    def partfract(self):
        """
        phi, Fraction of emissions in control regime
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            np.linspace(self.partfract1, self.partfract1, 1),
            self.partfract21 + (self.partfract2 - self.partfract21) * np.exp(
                -self.dpartfract * np.arange(23)),
            np.linspace(self.partfract21, self.partfract21, 36),
        ))

    @property
    def forcoth(self):
        """
        F_EX, Exogenous forcing for other greenhouse gases
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            self.fex0 + .1 * (self.fex1 - self.fex0) * np.arange(11),
            self.fex0 + (np.ones(49) * .36),
        ))

    @property
    def lam(self):
        return self.fco22x / self.t2xco2.value

    @property
    def tax_rate(self):
        """
        Carbon tax rate
        ...
        Returns
        -------
        float : backstop * 1000 * miu**(expcost2-1)
        """
        return self.backstop * 1000 * self.data['vars']['miu'] ** (
            self.expcost2.value - 1)

    @property
    def output_abate(self):
        """
        Abatement as a percentage of output
        ...
        Returns
        -------
        float : gcost1 * miu**expcost2
        """
        return self.data['vars']['gcost1'] * self.data['vars']['miu'] ** \
            self.expcost2.value

    @property
    def welfare(self):
        return np.sum(self.data['vars']['utility_d'])

    def step(self, i, D, miu=None, deriv=False, epsilon=1e-3, f0=0.0,
             scc=False):
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
        ...
        Returns
        -------
        None
        """
        ii = i - 1
        if i > 0:
            D['sigma'][i] = D['sigma'][ii] / (1 - self.gsig[i])
            D['al'][i] = D['al'][ii] / (1 - self.ga[ii])
            D['capital'][i] = self.eq.capital(
                D['capital'][ii], self.dk.value, D['investment'][ii]
            )
        D['gcost1'][i] = (self._pback * D['sigma'][i] / self.expcost2.value) * (
            (self.backrat.value - 1 + np.exp(-self.gback.value * i)) /
            self.backrat.value
        )
        D['gross_output'][i] = self.eq.gross_output(
            D['al'][i], D['capital'][i], self._gama, self.l[i]
        )
        if self.optimize:
            if miu is not None:
                if deriv:
                    D['miu'] = miu
                    D['miu'][i] = D['miu'][i] + epsilon
                else:
                    D['miu'][i] = miu[i]
        else:
            if i > 0:
                if self.treaty_switch.value:
                    D['miu'][i] = self.eq.miu(
                        D['emissions_ind'][ii], self.ecap[ii],
                        D['emissions_ind'][0],
                        D['sigma'][i], D['gross_output'][i]
                    )
                else:
                    D['miu'][i] = 0.
        D['emissions_ind'][i] = self.eq.emissions_ind(
            D['sigma'][i], D['miu'][i], D['gross_output'][i]
        )
        # D['emissions_total'][i] = self.eq.emissions_total(
        #     D['emissions_ind'][i], self.etree[i]
        # )
        if scc is True:
            D['emissions_total'][i] = (
                self.data['vars']['emissions_total'][i] + 1.0
            )
        else:
            D['emissions_total'][i] = self.eq.emissions_total(
                D['emissions_ind'][i], self.etree[i]
            )
        if i > 0:
            D['carbon_emitted'][i] = (
                D['carbon_emitted'][ii] + D['emissions_total'][i] * 10
            )
        else:
            D['carbon_emitted'][i] = 10 * D['emissions_total'][i]
        if D['carbon_emitted'][i] > self.fosslim.value:
            D['miu'][i] = 1
            D['emissions_total'][i] = 0
            D['carbon_emitted'][i] = self.fosslim.value
        if i > 0:
            D['mass_atmosphere'][i] = self.eq.mass_atmosphere(
                D['emissions_total'][ii], D['mass_atmosphere'][ii],
                D['mass_upper'][ii], self.bb
            )
            D['mass_upper'][i] = self.eq.mass_upper(
                D['mass_atmosphere'][ii], D['mass_upper'][ii],
                D['mass_lower'][ii], self.bb
            )
            D['mass_lower'][i] = self.eq.mass_lower(
                D['mass_upper'][ii], D['mass_lower'][ii], self.bb
            )
        D['forcing'][i] = self.eq.forcing(
            self.fco22x, D['mass_atmosphere'][i], self.matPI,
            self.forcoth[i]
        )
        if i > 0:
            D['temp_atmosphere'][i] = self.eq.temp_atmosphere(
                D['temp_atmosphere'][ii], D['temp_lower'][ii],
                D['forcing'][i], self.lam, self.cc
            )
            D['temp_lower'][i] = self.eq.temp_lower(
                D['temp_atmosphere'][ii], D['temp_lower'][ii], self.cc
            )
        D['damage'][i] = self.eq.damage(
            D['gross_output'][i], D['temp_atmosphere'][i], self.aa
        )
        D['abatement'][i] = self.eq.abatement(
            D['gross_output'][i], D['miu'][i], D['gcost1'][i],
            self.expcost2.value, self.partfract[i]
        )
        D['output'][i] = self.eq.output(
            D['gross_output'][i], D['damage'][i], D['abatement'][i]
        )
        if i == 0:
            D['investment'][i] = self.savings.value * self._q0
        else:
            D['investment'][i] = self.eq.investment(
                self.savings.value, D['output'][i]
            )
        D['consumption'][i] = self.eq.consumption(
            D['output'][i], self.savings.value
        )
        D['consumption_pc'][i] = self.eq.consumption_pc(
            D['consumption'][i], self.l[i]
        )
        D['utility'][i] = self.eq.utility(
            D['consumption_pc'][i], self.elasmu.value, self.l[i]
        )
        D['utility_d'][i] = self.eq.utility_d(
            D['utility'][i], self.rr[i], self.l[i]
        )
        if deriv:
            self.derivative['fprime'][i] = (D['utility_d'][i] - f0) / epsilon
            D['miu'] = self.data['vars']['miu']

    def loop(self, miu=None, deriv=False, scc=True):
        """
        Loop through step function for calculating endogenous variables
        """
        D = self.data['vars']
        _epsilon = 1e-4
        if self.optimize and miu is None:
            D['miu'] = self.get_ipopt_mu()
            D['miu'][0] = self.miu_2005
        for i in range(self.tmax):
            self.step(i, D, miu)
            if self.optimize and deriv:
                f0 = np.atleast_1d(D['utility_d'][i])
                self.step(
                    i, self.data['deriv'], miu=miu, epsilon=_epsilon,
                    deriv=True, f0=f0
                )
        if self.optimize and miu is not None:
            if deriv:
                return self.derivative['fprime'].transpose()
            else:
                return self.data['vars']['utility_d'].sum()
        if scc:
            periods = 20
            for i in range(periods):
                tail = self.tmax - periods
                last = i + tail
                S = self.data['vars'].copy()
                for j in range(self.tmax):
                    if j >= i:
                        shock = False
                        if j == i:
                            shock = True
                        self.step(j, S, miu=miu, scc=shock)
                D['scc'][i] = np.sum(
                    ((self.data['vars']['consumption_pc'][i:last] -
                        S['consumption_pc'][i:last]) * self.rr[:tail])
                ) * 10000. * (12./44.)

    def get_ipopt_mu(self):
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
            output += '%s %s\n' % (v, vv.value)
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
        x.value = getattr(x, value)
    d.loop()
    filename = '../verify/gams_%s_%s.csv' % (param, value)
    exclude = [
        'output_abate',
        'tax_rate',
        'backstop', 'l'
    ]
    with open(filename, 'a') as f:
        for i in range(d.tmax):
            for v in range(len(d.vars)):
                if d.vars[v] not in exclude:
                    f.write(str(round(d.data['vars'][d.vars[v]][i], 2)))
                    if v == (len(d.vars) - 1):
                        f.write('\n')
                    else:
                        f.write(',')

if __name__ == '__main__':
    exclude = ['e2050', 'e2100', 'e2150', ]
    # d = Dice2007(optimize=True)
    d = Dice2007()
    verify_out(d)
    for p in d.user_params:
        if p not in exclude:
            verify_out(d, p, 'minimum')
            verify_out(d, p, 'maximum')