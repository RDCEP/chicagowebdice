import numpy as np
from params import Dice2007Params
import equations
from scipy.optimize import minimize
import pyipopt
try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
except: pass

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
        Population growth factor
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
        if optimize: self.optimize = True
        self.POW = 1.0
        self.RAMP = False
        self.CLAMP = False
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
            'capital', 'gross_output', 'emissions_industrial',
            'emissions_total', 'mass_atmosphere', 'mass_upper',
            'mass_lower', 'forcing', 'temp_atmosphere',
            'temp_lower', 'damage', 'abatement', 'output', 'output_abate',
            'investment', 'carbon_emitted', 'consumption',
            'consumption_percapita', 'utility', 'utility_discounted',
            'al', 'gcost1', 'sigma', 'miu', 'backstop', 'l', 'tax_rate',
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
        return self._pop0 * (1 - self.gfacpop) + self.gfacpop * self.popasym.value
    @property
    def ga(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array : ga(0) * exp(-dela * 10 * t)
        """
        return self._ga0 * np.exp(-(self.dela.value/100.) * 10 * self.t0)
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
            self.dsig.value/100) * 10 * self.t0 - self.dsig2 * 10 * (self.t0 ** 2))
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
            (self.backrat.value - 1 + np.exp(-self.gback.value * self.t0)) / self.backrat.value)
    @property
    def etree(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array : Eland(0) * (1 - .1)^t
        """
        return self._eland0 * (1 - .1)**self.t0
    @property
    def rr(self):
        """
        R, Average utility social discount rate
        ...
        Returns
        -------
        array : 1 / (1 + prstp)^t
        """
        return 1 / ((1 + self.prstp.value)**(10*self.t0))
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
            (np.ones(5) * (100.-self.e2050.value)) / 100.,
            (np.ones(5) * (100.-self.e2100.value)) / 100.,
            (np.ones(45) * (100.-self.e2150.value)) / 100.,
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
            self.fex0 + (np.ones(49)*.36),
            ))
    @property
    def lam(self):
        return self.fco22x / self.t2xco2.value
    @property
    def tax_rate(self):
        return self.backstop * 1000 * self.data['vars']['miu'] ** (self.expcost2.value-1)
    @property
    def output_abate(self):
        return self.data['vars']['gcost1'] * self.data['vars']['miu']**self.expcost2.value
    @property
    def welfare(self):
        return np.sum(self.data['vars']['utility_discounted'])

    def step(self, i, D, miu=None, deriv=False, epsilon=1e-3, f0=0.0, slsqp=False):
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
        slsqp : boolean
        ...
        Returns
        -------
        None
        """
        if i > 0:
            D['sigma'][i] = D['sigma'][i-1] / (1 - self.gsig[i])
            D['al'][i] = D['al'][i-1] / (1 - self.ga[i-1])
            D['capital'][i] = self.eq.capital(D['capital'][i-1], self.dk.value,
                D['investment'][i-1])
        D['gcost1'][i] = (self._pback * D['sigma'][i] / self.expcost2.value) * (
            (self.backrat.value - 1 + np.exp(-self.gback.value * i)) / self.backrat.value)
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
                        D['emissions_industrial'][i-1], self.ecap[i-1],
                        D['emissions_industrial'][0],
                        D['sigma'][i], D['gross_output'][i]
                    )
                else: D['miu'][i] = 0.
        D['emissions_industrial'][i] = self.eq.emissions_industrial(
            D['sigma'][i], D['miu'][i], D['gross_output'][i]
        )
        D['emissions_total'][i] = self.eq.emissions_total(
            D['emissions_industrial'][i], self.etree[i]
        )
        if i > 0:
            D['carbon_emitted'][i] = (
                D['carbon_emitted'][i-1] + D['emissions_total'][i]
                )
        if D['carbon_emitted'][i] > self.fosslim:
            D['miu'][i] = 1
            D['emissions_total'][i] = 0
            D['carbon_emitted'][i] = self.fosslim
        if i > 0:
            D['mass_atmosphere'][i] = self.eq.mass_atmosphere(
                D['emissions_total'][i-1], D['mass_atmosphere'][i-1],
                D['mass_upper'][i-1], self.bb
            )
            D['mass_upper'][i] = self.eq.mass_upper(
                D['mass_atmosphere'][i-1], D['mass_upper'][i-1],
                D['mass_lower'][i-1], self.bb
            )
            D['mass_lower'][i] = self.eq.mass_lower(
                D['mass_upper'][i-1], D['mass_lower'][i-1], self.bb
            )
        D['forcing'][i] = self.eq.forcing(
            self.fco22x, D['mass_atmosphere'][i], self.matPI,
            self.forcoth[i]
        )
        if i > 0:
            D['temp_atmosphere'][i] = self.eq.temp_atmosphere(
                D['temp_atmosphere'][i-1], D['temp_lower'][i-1],
                D['forcing'][i], self.lam, self.cc
            )
            D['temp_lower'][i] = self.eq.temp_lower(
                D['temp_atmosphere'][i-1], D['temp_lower'][i-1], self.cc
            )
        D['damage'][i] = self.eq.damage(
            D['gross_output'][i], D['temp_atmosphere'][i], self.aa
        )
        D['abatement'][i] = self.eq.abatement(
            D['gross_output'][i], D['miu'][i], D['gcost1'][i],
            self.expcost2.value, self.partfract[i]
        )
        D['output'][i] = self.eq.output(D['gross_output'][i],
            D['damage'][i], D['abatement'][i])
        if i == 0:
            D['investment'][i] = self.savings.value * self._q0
        else:
            D['investment'][i] = self.eq.investment(self.savings.value, D['output'][i])
        D['consumption'][i] = self.eq.consumption(D['output'][i], self.savings.value)
        D['consumption_percapita'][i] = self.eq.consumption_percapita(
            D['consumption'][i], self.l[i]
        )
        D['utility'][i] = self.eq.utility(D['consumption_percapita'][i],
            self.elasmu.value, self.l[i])
        D['utility_discounted'][i] = self.eq.utility_discounted(
            D['utility'][i], self.rr[i], self.l[i]
        )
        if deriv:
            if slsqp:
                self.derivative[i] = (-D['utility_discounted'][i] + f0) / epsilon
            else:
#                self.derivative[i] = (D['utility_discounted'][:i+1].sum() - f0) / epsilon
                self.derivative[i] = (D['utility_discounted'][i] - f0) / epsilon
#            I = D['temp_lower'][i]
#            self.data['deriv'] = self.data['vars']
#            print I, D['temp_lower'][i]

    def loop(self, miu=None, slsqp=(False, False), deriv=False):
        """
        Loop through step function for calculating endogenous variables
        """
        D = self.data['vars']
        _epsilon = 1e-4
        if self.optimize and miu is None:
            D['miu'] = self.get_opt_mu()
#            D['miu'] = np.concatenate((
#                np.array([.005, .158, .184, .211, .240, .270, .302, .335, .370,
#                .407, .446, .486, .531, .577, .626, .678, .735, .795, .860, .931]),
#                np.ones(40)
#            ))
            D['miu'][0] = self.miu_2005
        if slsqp[1] or deriv:
            self.derivative = np.zeros([len(miu), 1])
        for i in range(self.tmax):
            self.step(i, self.data['vars'], miu)
            if self.optimize and (deriv or slsqp[1]):
                f0 = np.atleast_1d(D['utility_discounted'][i])
#                f0 = np.atleast_1d(D['utility_discounted'][:i+1].sum())
                self.step(i, self.data['deriv'], miu=miu, epsilon=_epsilon,
                    deriv=True, slsqp=slsqp[0], f0=f0)
        if self.optimize and miu is not None:
            if deriv:
#                print self.derivative.transpose()
                return self.derivative.transpose()
            elif slsqp[1]:
                return [
                    -self.data['vars']['utility_discounted'].sum(),
                    self.derivative.transpose(),
                ]
            else:
                if slsqp[0]:
                    return -self.data['vars']['utility_discounted'].sum()
                else:
                    return self.data['vars']['utility_discounted'].sum()

    def get_ramp(self):
        self.optimize = False
        self.loop()
        ramp = np.abs(
            (self.data['vars']['damage'] /
             self.data['vars']['consumption_percapita'])-.5
        ).argmin()
        if self.gback.value >= .1:
            ramp = int(round(ramp * .9))
        self.optimize = True
        return ramp

    def get_opt_mu(self):
        if self.RAMP:
            ramp = self.get_ramp()
            x0 = np.concatenate((
                np.linspace(.1, 1, ramp),
                np.ones(self.tmax-ramp)
            ))
        else:
            ramp = self.tmax - 1
            x0 = np.ones(self.tmax)
        x0 = self.get_ipopt_mu(x0, ramp)
        return x0

    def get_lbfgsb_mu(self, x):
        from scipy.optimize import fmin_l_bfgs_b
        BOUNDS = [(1e-8, 1.0)] * 60
        def f(x, slsqp):
            return self.loop(x, slsqp=slsqp, deriv=False)
        def g(x):
            return self.loop(x, slsqp=(True, True), deriv=False)[1]
        r = fmin_l_bfgs_b(f, x, fprime=None, args=((True, False),), approx_grad=True,
            bounds=BOUNDS, m=4, factr=1e-10, pgtol=1e-4, disp=2, maxfun=4,
            epsilon=1e-8)
        return r[0]

    def get_slsqp_mu(self, x0, ftol, rounds):
        DERIV = (True, False)
        ARGS = (DERIV, )
        OPTS = {'disp': False, 'maxiter': 10, }
        BOUNDS = [(0.0, 1.0)] * 30 + [(1.0, 1.0)] * 30
        for i in range(rounds):
            if i < 3: tol = 1.0/10.0**(i)
            else: tol = ftol
            OPTS['ftol'] = tol
            r = minimize(self.loop, x0, args=ARGS, method='SLSQP',
                bounds=BOUNDS, options=OPTS, jac=DERIV[1]
            )
            x0 = r.x
        return x0

    def get_openopt_mu(self, ftol):
        from openopt import GLP, NLP
        RAMP = 30
        x0 = np.concatenate((
            np.linspace(0,1,RAMP),
            np.ones(self.tmax-RAMP),
            ))
        x0 = np.ones(self.tmax)
        ub = np.ones(self.tmax)
        lb = np.zeros(self.tmax)
        fun = self.loop
        def grad(x):
            return self.loop(x, deriv=True)
        p = NLP(fun, x0, lb=lb, ub=ub, iprint=1, df=grad)
        r = p.solve('ipopt', gtol=.0001, maxIter=10, optFile='./ipopt.opt',)
        return r.xf

    def get_ipopt_mu(self, x0, RAMP, *args, **kwargs):
        M = 0
        xl = np.zeros(self.tmax)
        if self.CLAMP:
            xl[RAMP:] = 1.
        xu = np.ones(self.tmax)
        gl = np.zeros(M)
        gu = np.ones(M)
        def eval_f(x):
            return self.loop(x)
        def eval_grad_f(x):
            return self.loop(x, deriv=True)
        def eval_g(x, user_data=None):
            print user_data
#            print user_data
            return np.zeros(M)
        def eval_jac_g(x, flag):
            if flag: return ([],[])
            else: return []
        def eval_h(x):
            return np.array([])
        nnzj = 0
        nnzh = 0
        r = pyipopt.create(self.tmax, xl, xu, M, gl, gu, nnzj, nnzh, eval_f,
            eval_grad_f, eval_g, eval_jac_g)
        x, zl, zu, obj, status = r.solve(x0)
        print 'Objective function: ', obj, '; Status: ', status
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

def profile_stub():
    d = Dice2007(optimize=True)
    try:
        VAR = 'utility_discounted'
        a = 58
        b = 60
        rcParams.update({'font.size': 6})
        fig1 = plt.figure(figsize=(5, 3.5), dpi=200)
        one = False
        two = True
        three = False
        four = True

        # RAMPED, UNCLAMPED
        if one:
            d.ONES = False; d.CLAMP = False
            d.loop()
            plt.subplot(211)
            plt.plot(d.data['vars']['miu'])
            plt.subplot(212)
            plt.plot(d.data['vars'][VAR][a:b])

        # ONES, UNCLAMPED
        if two:
            d.ONES = True; d.CLAMP = False
            d.loop()
            plt.subplot(211)
            plt.plot(d.data['vars']['miu'])
            plt.subplot(212)
            plt.plot(d.data['vars'][VAR][a:b])

        # RAMPED, CLAMPED
        if three:
            d.ONES = False; d.CLAMP = True
            d.loop()
            plt.subplot(211)
            plt.plot(d.data['vars']['miu'])
            plt.subplot(212)
            plt.plot(d.data['vars'][VAR][a:b])

        # UNOPTIMIZED
        if four:
            d.optimize = False
            d.loop()
            plt.subplot(211)
            plt.plot(d.data['vars']['miu'])
            plt.subplot(212)
            plt.plot(d.data['vars'][VAR][a:b])
            print d.welfare
        plt.show()
#        print d.data['vars']['temp_lower'] - d.data['deriv']['temp_lower']
    except:
        pass

if __name__ == '__main__':
    profile_stub()