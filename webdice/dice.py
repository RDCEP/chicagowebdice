import nlopt
from numpy import *
from datetime import datetime
import numpy as np
from params import Dice2007Params
import equations
from scipy.optimize import minimize

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
    def __init__(self, time_travel=True, optimize=False):
        self.eq = equations.default.Loop()
        Dice2007Params.__init__(self)
        self.p = Dice2007Params()
        self.optimize = False
        if optimize: self.optimize = True
    #    , if time_travel:
    #            self.eq.forcing = excel.ExcelLoop.forcing
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
            'temp_lower', 'damage', 'abatement', 'output',
            'investment', 'carbon_emitted', 'consumption',
            'consumption_percapita', 'utility', 'utility_discounted',
            'al', 'gcost1', 'sigma', 'miu', 'backstop',
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
    def welfare(self):
        return np.sum(self.utility_discounted)

    def loop(self, miu=None, opt=True, obj_mult=100., obj_tol=.1):
        """
        Step function for calculating endogenous variables
        """
        if self.optimize and miu is None:
            self.miu = self.get_opt_mu(obj_tol)
            self.miu[0] = self.miu_2005
        for i in range(self.tmax):
            if i > 0:
                self.sigma[i] = self.sigma[i-1] / (1 - self.gsig[i])
                self.al[i] = self.al[i-1] / (1 - self.ga[i-1])
                self.capital[i] = self.eq.capital(self.capital[i-1], self.dk.value,
                    self.investment[i-1])
            self.gcost1[i] = (self._pback * self.sigma[i] / self.expcost2.value) * (
                (self.backrat.value - 1 + np.exp(-self.gback.value * i)) / self.backrat.value)
            self.gross_output[i] = self.eq.gross_output(
                self.al[i], self.capital[i], self._gama, self.l[i]
            )
            if self.optimize:
                if miu is not None:
                    if i > 0:
                        self.miu[i] = miu[i]
                    else:
                        self.miu[i] = self.miu_2005
            else:
                if i > 0:
                    if self.treaty_switch.value:
                        self.miu[i] = self.eq.miu(
                            self.emissions_industrial[i-1], self.ecap[i-1],
                            self.emissions_industrial[0],
                            self.sigma[i], self.gross_output[i]
                        )
                    else: self.miu[i] = 0.
            self.emissions_industrial[i] = self.eq.emissions_industrial(
                self.sigma[i], self.miu[i], self.gross_output[i]
            )
            self.emissions_total[i] = self.eq.emissions_total(
                self.emissions_industrial[i], self.etree[i]
            )
            if i > 0:
                self.carbon_emitted[i] = (
                    self.carbon_emitted[i-1] + self.emissions_total[i]
                    )
            if self.carbon_emitted[i] > self.fosslim:
                self.miu[i] = 1
                self.emissions_total[i] = 0
                self.carbon_emitted[i] = self.fosslim
            if i > 0:
                self.mass_atmosphere[i] = self.eq.mass_atmosphere(
                    self.emissions_total[i-1], self.mass_atmosphere[i-1],
                    self.mass_upper[i-1], self.bb
                )
                self.mass_upper[i] = self.eq.mass_upper(
                    self.mass_atmosphere[i-1], self.mass_upper[i-1],
                    self.mass_lower[i-1], self.bb
                )
                self.mass_lower[i] = self.eq.mass_lower(
                    self.mass_upper[i-1], self.mass_lower[i-1], self.bb
                )

            ma2 = self.eq.mass_atmosphere(
                self.emissions_total[i],self.mass_atmosphere[i],
                self.mass_upper[i], self.bb
            )
            self.forcing[i] = self.eq.forcing(
                self.fco22x, self.mass_atmosphere[i], self.matPI,
                self.forcoth[i], ma2
            )
            if i > 0:
                self.temp_atmosphere[i] = self.eq.temp_atmosphere(
                    self.temp_atmosphere[i-1], self.temp_lower[i-1],
                    self.forcing[i], self.lam, self.cc
                )
                self.temp_lower[i] = self.eq.temp_lower(
                    self.temp_atmosphere[i-1], self.temp_lower[i-1], self.cc
                )
            self.damage[i] = self.eq.damage(
                self.gross_output[i], self.temp_atmosphere[i], self.aa
            )
            self.abatement[i] = self.eq.abatement(
                self.gross_output[i], self.miu[i], self.gcost1[i],
                self.expcost2.value, self.partfract[i]
            )
            self.output[i] = self.eq.output(self.gross_output[i],
                self.damage[i], self.abatement[i])
            if i == 0:
                self.investment[i] = self.savings.value * self._q0
            else:
                self.investment[i] = self.eq.investment(self.savings.value, self.output[i])
            self.consumption[i] = self.eq.consumption(self.output[i], self.savings.value)
            self.consumption_percapita[i] = self.eq.consumption_percapita(
                self.consumption[i], self.l[i]
            )
            self.utility[i] = self.eq.utility(self.consumption_percapita[i],
                self.elasmu.value, self.l[i])
            self.utility_discounted[i] = self.eq.utility_discounted(
                self.utility[i], self.rr[i], self.l[i]
            )
        if self.optimize and miu is not None:
            return [
                obj_mult * (0 - self.utility_discounted.sum()),
                np.gradient(self.utility_discounted),
            ]

    def get_opt_mu(self, ftol):
        RAMP = 30
        x0 = np.concatenate((
            np.linspace(0,1,RAMP),
            np.ones(self.tmax-RAMP),
        ))
        SOLVER='SLSQP'
        ARGS = (True,1.,)
        OPTS = {
            'disp': False,
            'ftol': ftol,
            'maxiter': 10,
            'eps': 1e-1,
        }
        xl = 1e-6
        xu = 1.
        BOUNDS = [(xl,xu)] * self.tmax
        def step(x0, tol=.1):
            OPTS['ftol'] = tol
            r = minimize(self.loop, x0, args=ARGS, method=SOLVER,
                bounds=BOUNDS, options=OPTS, jac=True
            )
            if __name__ == '__main__': print r.fun
            return r.x
        for i in range(5):
            if i < 3: tol=1./10**i
            else: tol = .01
            x0 = step(x0, tol=tol)
        if __name__ == '__main__': print x0
        return x0

    def format_output(self):
        """Output text for Google Visualizer graph functions."""
        #TODO: This is sloppy as shit.
        output = ''
        for v in self.user_params:
            vv = getattr(self, v)
            output += '%s %s\n' % (v, vv.value)
        for v in self.vars:
            vv = getattr(self, v)
            output += '%s %s\n' % (v, ' '.join(map(str, list(vv))))
        return output

#if __name__ == '__main__':
def profile_stub():
    d = Dice2007(optimize=True)
    t0 = datetime.now()
    d.loop(opt=True, obj_mult=1., obj_tol=.01)
    t1 = datetime.now()
    print t1-t0

if __name__ == '__foo__':
    import argparse
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] variables')
    var_help = """
    You can print the following: capital, gross_output, emissions_industrial,
    emissions_total, mass_atmosphere, mass_lower, mass_upper, forcing,
    temp_atmosphere, temp_lower, damage, abatement, output, investment,
    carbon_emitted, consumption, consumption_percapita, utility,
    utility_discounted, and welfare.
    """
    parser.add_argument('variables', help=var_help, metavar='var1[,var2[,...]]')
    args = parser.parse_args()
    d = [Dice2007()]
    for m in d:
        m.loop()
    try:
        for v in args.variables.split(','):
            try:
                for m in d:
                    print bcolors.HEADER, '%s %s:\n' % (
                        m.eq.__module__.split('.')[1], v
                        ), bcolors.ENDC, getattr(m, v)
            except:
                print bcolors.WARNING, 'No variable named %s' % v, bcolors.ENDC
    except:
        print 'No variables specified'
        print 'You can print the following: capital, gross_output, emissions_industrial,'
        print 'emissions_total, mass_atmosphere, mass_lower, mass_upper, forcing,'
        print 'temp_atmosphere, temp_lower, damage, abatement, output, investment,'
        print 'carbon_emitted, consumption, consumption_percapita, utility,'
        print 'utility_discounted, and welfare'
