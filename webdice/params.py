import numpy as np

class diceParams(object):
    def __init__(self):
        self.elasmu = 2.0 # Elasticity of marginal utility of consumption
        self.prstp = .015 # Initial rate of social time preference per year
        ## Population and technology
        self._pop0 = 6514. # 2005 world population millions
        self._gpop0 = .35 # growth rate of population per decade
        self.popasym = 8600. # asymptotic population
        self._a0 = .02722 # Initial level of total factor productivity
        self._ga0 = .092 # Initial growth rate for technology per decade
        self.dela = .1 # Decline rate of technological change per decade
        self.dk = .100 # Depreciation rate on capital per year
        self._gama = .300 # Capital elasticity in production function
        self._q0 = 61.1 # 2005 world gross output trill 2005 US dollars
        self._k0 = 137. # 2005 value capital trill 2005 US dollars
        ## Emissions
        self._sig0 = .13418 # CO2-equivalent emissions-GNP ratio 2005 (effectively intensity)
        self._gsigma = -.0730 # Initial growth of sigma per decade
        self.dsig = .3 # Decline rate of decarbonization per decade
        self.dsig2 = .000 # Quadratic term in decarbonization
        self._eland0 = 1.1000 # Carbon emissions from land 2005 (GtC per decade)
        self._e2005 = 84.1910 # Year 2005 Emissions
        ## Carbon Cycle
        self.mat2000 = 808.9 # Concentration in atmosphere 2005 (GtC)
        self.mu2000 = 1255. # Concentration in upper strata 2005 (GtC)
        self.ml2000 = 18365. # Concentration in lower strata 2005 (GtC)
        self.matPI = 278. * 2.13 # Preindustrial concentration in atmosphere 2005 (GtC)
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
        self.bb = np.array([self.b11, self.b12, self.b13, self.b21, self.b22, self.b23, self.b31, self.b32, self.b33]).reshape(3,3)
        ## Climate model
        self.t2xco2 = 3. # Equilibrium temp impact of CO2 doubling (degrees C)
        self.fex0 = -.06 # Estimate of 2000 forcings of non-CO2 GHG
        self.fex1 = .30 # Estimate of 2100 forcings of non-CO2 GHG
        self.tocean0 = .0068 # 2000 lower strat. temp change (C) from 1900
        self.tatm0 = .7307 # 2000 atmospheric temp change (C) from 1900
        self.c1 = .220
        self.c2 = 0
        self.c3 = .300
        self.c4 = .050
#        self.cc = np.array([.220, 0, .300, .050])
        self.cc = np.array([self.c1, self.c2, self.c3, self.c4])
        self.fco22x = 3.8 # Estimated forcings of equilibrium CO2 doubling
        # Climate damage selfeters, calibrated for quadratic at 2.5 C for 2105
#        self.aa = np.array([0, 0.0028388, 2])
        self.a1 = 0
        self.a2 = 0.0028388
        self.a3 = 2
        ## Abatement cost
        self.expcost2 = 2.8 # Exponent of control cost function
        self._pback = 1.17 # Cost of backstop 2005, thousands of $ per tC 2005
        self.backrat = 2. # Ratio initial to final backstop cost
        self.gback = .05 # Initial cost decline backstop, # per decade
        self.limmiu = 1. # Upper limit on control rate
        ## Participation
        self.partfract1 = 1. # Fraction of emissions under control regime 2005
        self.partfract2 = 1. # Fraction of emissions under control regime 2015
        self.partfract21 = 1. # Fraction of emissions under control regime 2205
        self.dpartfract = 0. # Decline rate of participation
        self.e2050 = 0.
        self.e2100 = 0.
        self.e2150 = 0.
        ## Availability of fossil fuels
        self.fosslim = 6000. # Maximum cumulative extraction fossil fuels
        ## Scaling and inessential selfeters
        self.scale1 = 194. # Scaling coefficient in the objective function
        self.scale2 = 381800. # Scaling coefficient in the objective function
        self.tmax = 60 # Time periods, in decades (60 * 10 = 600 years)
        self.numScen = 1 # Number of scenarios to run
        self.savings = .22 # Savings rate (constant)
        self.miu_2005 = .005 # emission control rate (fraction of uncontrolled emissions)
        self.t0 = np.linspace(0, self.tmax-1, self.tmax)
        self.t1 = self.t0 + 1
    def update_exos(self):        
        self.lam = self.fco22x / self.t2xco2
        self.sigma = np.linspace(self._sig0, self._sig0, self.tmax)
        self.al = np.linspace(self._a0, self._a0, self.tmax)
        self.capital = np.linspace(self._k0, self._k0, self.tmax)
        self.output = np.linspace(self._q0, self._q0, self.tmax)
        self.mass_atmosphere = np.linspace(self.mat2000, self.mat2000, self.tmax)
        self.mass_upper = np.linspace(self.mu2000, self.mu2000, self.tmax)
        self.mass_lower = np.linspace(self.ml2000, self.ml2000, self.tmax)
        self.temp_atmosphere = np.linspace(self.tatm0, self.tatm0, self.tmax)
        self.temp_lower = np.linspace(self.tocean0, self.tocean0, self.tmax)
        self.gross_output = np.zeros(self.tmax)
        self.forcing = np.zeros(self.tmax)
        self.emissions_industrial = np.zeros(self.tmax)
        self.emissions_total = np.zeros(self.tmax)
        self.carbon_emitted = np.zeros(self.tmax)
        self.participation = np.zeros(self.tmax)
        self.participation_markup = np.zeros(self.tmax)
        self.damage = np.zeros(self.tmax)
        self.abatement = np.zeros(self.tmax)
        self.investment = np.linspace(self.savings * self._q0, self.savings * self._q0,self.tmax)
        self.consumption = np.zeros(self.tmax)
        self.consumption_percapita = np.zeros(self.tmax)
        self.utility = np.zeros(self.tmax)
        self.utility_discounted = np.zeros(self.tmax)
        self.miu = np.linspace(self.miu_2005, self.miu_2005, self.tmax)
        self.pref_fac = np.ones(self.tmax)