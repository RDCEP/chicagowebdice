import numpy as np
import pandas as pd


class Dice2007Params(object):
    def __init__(self):
        self.t2xco2 = 3.
        self.a3 = 2.
        self.dela = .1
        self.dsig = .3
        self.expcost2 = 2.8
        self.gback = .05
        self.backrat = 2.
        self.popasym = 8600.
        self.dk = .1
        self.savings = .2
        self.fosslim = 6000.
        self.carbon_model = 'dice_carbon'
        self.damages_model = 'dice_output'
        self.elasmu = 2.
        self.prstp = .015
        self.treaty_switch = False
        self.e2050 = 100.
        self.e2100 = 100.
        self.e2150 = 100.
        self.p2050 = 100.
        self.p2100 = 100.
        self.p2150 = 100.
        self.pmax = 100.
        self.c2050 = 0.
        self.c2100 = 0.
        self.c2150 = 0.
        self.cmax = 500.
        ## Population and technology
        self._pop0 = 6514.  # 2005 world population millions
        self._gpop0 = .35  # growth rate of population per decade
        self._a0 = .02722  # Initial level of total factor productivity
        self._ga0 = .092  # Initial growth rate for technology per decade
        self._gama = .300  # Capital elasticity in production function
        self._q0 = 61.1  # 2005 world gross output trill 2005 US dollars
        self._q0 = 55.667  # 2005 world gross output trill 2005 US dollars
        self._k0 = 137.  # 2005 value capital trill 2005 US dollars
        self.prod_fac = .05

        ## Emissions
        self._sig0 = .13418  # CO2-equivalent emissions-GNP ratio 2005
        self._gsigma = -.0730  # Initial growth of sigma per decade
        self.dsig2 = .000  # Quadratic term in decarbonization
        self._eland0 = 11.0  # Carbon emissions from land 2005 (GtC per decade)

        ## Carbon Cycle
        self.mat2000 = 808.9  # Concentration in atmosphere 2005 (GtC)
        self.mu2000 = 1255.  # Concentration in upper strata 2005 (GtC)
        self.ml2000 = 18365.  # Concentration in lower strata 2005 (GtC)
        self.matPI = 278. * 2.13  # Preindustrial conc. in atmosphere 2005 (GtC)
        # Carbon cycle transition matrix
        self.b11 = .810712
        self.b12 = .189288
        self.b13 = 0
        self.b21 = .097213
        self.b22 = .852787
        self.b23 = .05
        self.b31 = 0
        self.b32 = .003119
        self.b33 = .996881
        self.bb = np.array([
            self.b11, self.b12, self.b13, self.b21, self.b22, self.b23,
            self.b31, self.b32, self.b33
        ]).reshape(3, 3)

        ## Climate model
        self.fex0 = -.06  # Estimate of 2000 forcings of non-CO2 GHG
        self.fex1 = .30  # Estimate of 2100 forcings of non-CO2 GHG
        self.tocean0 = .0068  # 2000 lower strat. temp change (C) from 1900
        self.tatm0 = .7307  # 2000 atmospheric temp change (C) from 1900
        self.c1 = .220
        self.c2 = 0
        self.c3 = .300
        self.c4 = .050
        self.cc = np.array([self.c1, self.c2, self.c3, self.c4])
        self.fco22x = 3.8  # Estimated forcings of equilibrium CO2 doubling
        # Climate damage selfeters, calibrated for quadratic at 2.5 C for 2105
        self.a1 = 0
        self.a2 = 0.0028388

        ## Abatement cost
        self._pback = 1.17  # Cost of backstop 2005, thousands of $ per tC 2005
        self.limmiu = 1.  # Upper limit on control rate

        ## Participation
        self.partfract1 = 1.  # Fraction of emissions under control regime 2005
        self.partfract2 = 1.  # Fraction of emissions under control regime 2015
        self.partfract21 = 1.  # Fraction of emissions under control regime 2205
        self.dpartfract = 0.  # Decline rate of participation

        ## Availability of fossil fuels
        ## Scaling and inessential selfeters
        self.scale1 = 194.  # Scaling coefficient in the objective function
        self.scale2 = 381800.  # Scaling coefficient in the objective function
        self.tmax = 60  # Time periods, in decades (60 * 10 = 600 years)
        self.numScen = 1  # Number of scenarios to run
        self.miu_2005 = .005  # emission control rate
        self.t0 = np.arange(float(self.tmax))
        self.t1 = self.t0 + 1

        # Variables for initiating pandas array
        gcost1 = np.zeros(self.tmax)
        sigma = np.empty(self.tmax)
        sigma[:] = self._sig0
        al = np.empty(self.tmax)
        al[:] = self._a0
        capital = np.empty(self.tmax)
        capital[:] = self._k0
        output = np.empty(self.tmax)
        output[:] = self._q0
        mass_atmosphere = np.empty(self.tmax)
        mass_atmosphere[:] = self.mat2000
        mass_upper = np.empty(self.tmax)
        mass_upper[:] = self.mu2000
        mass_lower = np.empty(self.tmax)
        mass_lower[:] = self.ml2000
        temp_atmosphere = np.empty(self.tmax)
        temp_atmosphere[:] = self.tatm0
        temp_lower = np.empty(self.tmax)
        temp_lower[:] = self.tocean0
        investment = np.empty(self.tmax)
        investment[:] = self.savings * self._q0
        miu = np.empty(self.tmax)
        miu[:] = self.miu_2005
        data = pd.DataFrame({
            'miu': miu,
            'sigma': sigma,
            'al': al,
            'gcost1': gcost1,
            'capital': capital,
            'output': output,
            'mass_atmosphere': mass_atmosphere,
            'mass_upper': mass_upper,
            'mass_lower': mass_lower,
            'temp_atmosphere': temp_atmosphere,
            'temp_lower': temp_lower,
            'investment': investment,
            'gross_output': np.zeros(self.tmax),
            'forcing': np.zeros(self.tmax),
            'emissions_ind': np.zeros(self.tmax),
            'emissions_total': np.zeros(self.tmax),
            'carbon_emitted': np.zeros(self.tmax),
            'participation': np.zeros(self.tmax),
            'participation_markup': np.zeros(self.tmax),
            'damage': np.zeros(self.tmax),
            'abatement': np.zeros(self.tmax),
            'consumption': np.zeros(self.tmax),
            'consumption_pc': np.zeros(self.tmax),
            'utility': np.zeros(self.tmax),
            'utility_d': np.zeros(self.tmax),
            'pref_fac': np.ones(self.tmax),
            'scc': np.ones(self.tmax),
        })
        self.data = pd.Panel({
            'vars': data,
            'deriv': data,
            'scc': data,
        })
        self.derivative = pd.DataFrame({
            'fprime': np.empty(self.tmax),
        })
        self.hessian = pd.Series(np.empty(self.tmax))