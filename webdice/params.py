import numpy as np

class DiceWebParam(object):
    def __init__(self, name, description, section, default,
                 minimum=None, maximum=None, precision=None, step=None, 
                 submit=None, select=None, unit=None, value=None,
                 disabled=False):
        self.name = name
        self.decription = description
        self.section = section
        self.default = default
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.precision = precision
        self.unit = unit
        self.submit = submit
        self.select = select
        self.disabled = disabled
        if not value:
            self.value = self.default

class DiceWebTab(object):
    def __init__(self, name):
        self.name = name

class DiceWebTabSection(object):
    def __init__(self, name, tab):
        self.name = name
        self.tab = tab

class Dice2007Params(object):
    def __init__(self):
        basic = DiceWebTab('Basic')
        advanced = DiceWebTab('Advanced')
        optimize = DiceWebTab('Optimization')

        beliefs = DiceWebTabSection(
            'Your beliefs about the climate and the future', basic
        )
        treaty = DiceWebTabSection(
            'Simulated climate treaty: Choose limitations on emissions (as a percent of 2005 emissions):', basic
        )
        emissions = DiceWebTabSection(
            'Costs of emissions control', advanced
        )
        additional = DiceWebTabSection(
            'Additional Parameters', advanced
        )
        model = DiceWebTabSection(
            'Model Design', advanced
        )
        additional2 = DiceWebTabSection(
            'Additional Parameters', optimize
        )
        run_opt = DiceWebTabSection(
            'Run Model', optimize
        )
        self.t2xco2 = DiceWebParam(
            'Climate sensitivity: How much will temperatures go up?', 
            'Temperature increase in degrees C from doubling of atmospheric CO2',
            beliefs, 3, minimum=1, maximum=5, step=.5, precision=1,
            unit='C'
        )
        self.a3 = DiceWebParam(
            'Exponent of damage function: How large will the harms be?',
            'Increase in harms from climate change due to an increase in temperatures',
            beliefs, 2, minimum=1, maximum=4, step=.5, precision=1, 
        )    
        self.dela = DiceWebParam(
            'How much will growth slow down in the future?',
            'Decline in the rate of growth in productivity over time',
            beliefs, .1, minimum=.05, maximum=1.5, step=.05, precision=2, 
            unit='%'
        )
        self.dsig = DiceWebParam(
            'Change in Energy intensity (higher number means more energy intensive)',
            'Rate of decline in energy use per $ of GDP',
            beliefs, .3, minimum=0, maximum=6, step=.1, precision=1, 
            unit='%'
        )
        self.e2050 = DiceWebParam(
            '2050', 'The mandated decrease in emissions by 2050 as a share of 2005 year emissions',
            treaty, 100, minimum=0, maximum=100, step=5, precision=0,
            unit='%'
        )
        self.e2100 = DiceWebParam(
            '2100', 'The mandated decrease in emissions by 2100 as a share of 2005 year emissions',
            treaty, 100, minimum=0, maximum=100, step=5, precision=0,
            unit='%'
        )
        self.e2150 = DiceWebParam(
            '2150', 'The mandated decrease in emissions by 2150 as a share of 2005 year emissions',
            treaty, 100, minimum=0, maximum=100, step=5, precision=0,
            unit='%'
        )
        self.expcost2 = DiceWebParam(
            'Marginal cost of abatement', 'Additional cost from more abatement',
            emissions, 2.8, minimum=2, maximum=4, step=.1, precision=1, 
        )
        self.gback = DiceWebParam(
            'Rate of decline of clean energy costs', 'Rate of decline in costs of reduction emissions',
            emissions, .05, minimum=0, maximum=.2, step=.05, precision=2, 
            unit='%'
        )
        self.backrat = DiceWebParam(
            'Ratio of current to future clean energy costs',
            'Cost of replacing all emissions in 2012 $ per ton of CO_{2} , relative to future cost',
            emissions, 2, minimum=.5, maximum=4, step=.5, precision=1, 
        )
        self.popasym = DiceWebParam(
            'Max population', 'Number, in billions, that the population grows asymptotically towards',
            additional, 8600, minimum=8000, maximum=12000, step=200, precision=0, 
            unit='billions',
        )
        self.dk = DiceWebParam(
            'Depreciation rate', 'Rate of depreciation per year',
            additional, .1, minimum=.08, maximum=.2, step=.02, precision=2, 
            unit='%',
        )
        self.savings = DiceWebParam(
            'Savings rate', 'Savings are per year',
            additional, .2, minimum=.15, maximum=.25, step=.05, precision=2, 
            unit='%',
        )
        self.fosslim = DiceWebParam(
            'Fossil fuel reserves', 'Fossil fuels remaining, measured in CO2 emissions',
            additional, 6000, minimum=6000, maximum=9000, step=500, precision=0, 
            unit=' Gt&nbsp;C',
        )
        self.oceanmodel = DiceWebParam(
            'Carbon cycle', 'Oceanic model of carbon transfer',
            model, 'dice_carbon', disabled=True, select=[{'name': 'DICE', 'machine_name': 'dice_carbon'}]
        )
        self.damages_model = DiceWebParam(
            'Damages model', 'Way that climate change harms enter the economy',
            model, 'dice', disabled=True, select=[{'name': 'DICE Damages to Gross Output',
                                           'machine_name': 'dice',
                                           'description': 'Climate change destroys a certain percentage of global output'}]
        )
        self.elasmu = DiceWebParam(
            'Elasticity of marg. consump.', 'Exponent of consumption in utility function',
            additional2, 2, minimum=1, maximum=3, step=.1, precision=1
        )
        self.prstp = DiceWebParam(
            'Pure rate of time preference', 'Discount rate applied to utility',
            additional2, .015, minimum=0, maximum=4, step=.005, precision=3
        )
        self.run_opt = DiceWebParam(
            'Run optimization', '', run_opt,
            'run-opt',  submit='Run'
        )
        self.treaty_switch = DiceWebParam(
            '', '', treaty, False
        )
        ## Population and technology
        self._pop0 = 6514. # 2005 world population millions
        self._gpop0 = .35 # growth rate of population per decade
        self._a0 = .02722 # Initial level of total factor productivity
        self._ga0 = .092 # Initial growth rate for technology per decade
        self._gama = .300 # Capital elasticity in production function
        self._q0 = 61.1 # 2005 world gross output trill 2005 US dollars
        self._k0 = 137. # 2005 value capital trill 2005 US dollars
        ## Emissions
        self._sig0 = .13418 # CO2-equivalent emissions-GNP ratio 2005 (effectively intensity)
        self._gsigma = -.0730 # Initial growth of sigma per decade
        self.dsig2 = .000 # Quadratic term in decarbonization
        self._eland0 = 1.1000 # Carbon emissions from land 2005 (GtC per decade)
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
        ## Abatement cost
        self._pback = 1.17 # Cost of backstop 2005, thousands of $ per tC 2005
        self.limmiu = 1. # Upper limit on control rate
        ## Participation
        self.partfract1 = 1. # Fraction of emissions under control regime 2005
        self.partfract2 = 1. # Fraction of emissions under control regime 2015
        self.partfract21 = 1. # Fraction of emissions under control regime 2205
        self.dpartfract = 0. # Decline rate of participation
        ## Availability of fossil fuels
        ## Scaling and inessential selfeters
        self.scale1 = 194. # Scaling coefficient in the objective function
        self.scale2 = 381800. # Scaling coefficient in the objective function
        self.tmax = 60 # Time periods, in decades (60 * 10 = 600 years)
        self.numScen = 1 # Number of scenarios to run
        self.miu_2005 = .005 # emission control rate (fraction of uncontrolled emissions)
        self.t0 = np.arange(float(self.tmax))
        self.t1 = self.t0 + 1
        self.gcost1 = np.zeros(self.tmax)
        self.sigma = np.empty(self.tmax); self.sigma[:] = self._sig0
        self.al = np.empty(self.tmax); self.al[:] = self._a0
        self.capital = np.empty(self.tmax); self.capital[:] = self._k0
        self.output = np.empty(self.tmax); self.output[:] = self._q0
        self.mass_atmosphere = np.empty(self.tmax); self.mass_atmosphere[:] = self.mat2000
        self.mass_upper = np.empty(self.tmax); self.mass_upper[:] = self.mu2000
        self.mass_lower = np.empty(self.tmax); self.mass_lower[:] = self.ml2000
        self.temp_atmosphere = np.empty(self.tmax); self.temp_atmosphere[:] = self.tatm0
        self.temp_lower = np.empty(self.tmax); self.temp_lower[:] = self.tocean0
        self.investment = np.empty(self.tmax); self.investment[:] = self.savings.value * self._q0
        self.miu = np.empty(self.tmax); self.miu[:] = self.miu_2005
        self.gross_output = np.zeros(self.tmax)
        self.forcing = np.zeros(self.tmax)
        self.emissions_industrial = np.zeros(self.tmax)
        self.emissions_total = np.zeros(self.tmax)
        self.carbon_emitted = np.zeros(self.tmax)
        self.participation = np.zeros(self.tmax)
        self.participation_markup = np.zeros(self.tmax)
        self.damage = np.zeros(self.tmax)
        self.abatement = np.zeros(self.tmax)
        self.investment = np.zeros(self.tmax)
        self.consumption = np.zeros(self.tmax)
        self.consumption_percapita = np.zeros(self.tmax)
        self.utility = np.zeros(self.tmax)
        self.utility_discounted = np.zeros(self.tmax)
        self.pref_fac = np.ones(self.tmax)