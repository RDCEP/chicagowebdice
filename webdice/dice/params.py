from __future__ import division
import numpy as np
import pandas as pd


class DiceUserParams(object):
    def __init__(self, model=2007):
        self.temp_co2_doubling = 3.
        self.damages_exponent = 2.
        self.productivity_decline = .001
        self.intensity_decline_rate = .003
        self.abatement_exponent = 2.8
        self.backstop_decline = .05
        self.backstop_ratio = 2.
        self.popasym = 8600.
        self.depreciation = .1
        self.savings = .22
        self.fosslim = 6000.
        self.carbon_model = 'dice_%s' % model
        self.consumption_model = 'dice_%s' % model
        self.damages_model = 'dice_%s' % model
        self.emissions_model = 'dice_%s' % model
        self.productivity_model = 'dice_%s' % model
        self.temperature_model = 'dice_%s' % model
        self.utility_model = 'dice_%s' % model
        self.prod_frac = .05
        self.elasmu = 2.
        self.prstp = .015
        self.e2050 = 1.
        self.e2100 = 1.
        self.e2150 = 1.
        self.p2050 = 1.
        self.p2100 = 1.
        self.p2150 = 1.
        self.c2050 = 0.
        self.c2100 = 0.
        self.c2150 = 0.


class DiceParams(DiceUserParams):
    def __init__(self, model=2007):
        DiceUserParams.__init__(self, model)
        self.dice_version = '2007'
        self.treaty = False
        self.carbon_tax = False
        self.pmax = 1.
        self.cmax = 500.

        ## Population and technology
        self.population_2005 = 6514.
        self.population_growth = .35
        self.productivity = .02722
        self.productivity_growth = .092
        self.output_elasticity = .300
        self.output_2005 = 61.1
        self.output_2005 = 55.667
        self.capital_2005 = 137.

        ## Emissions
        self.intensity_2005 = .13418
        self.intensity_growth = -.0730
        self.intensity_quadratic = .000
        self.emissions_deforest_2005 = 1.1

        ## Carbon Cycle
        _b11, _b12, _b13 = .810712, .189288, 0
        _b21, _b22, _b23 = .097213, .852787, .05
        _b31, _b32, _b33 = 0, .003119, .996881
        self.carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self.mass_atmosphere_2005 = 808.9
        self.mass_upper_2005 = 1255.
        self.mass_lower_2005 = 18365.
        self.mass_preindustrial = 592.14

        ## Climate model
        self.forcing_ghg_2000 = -.06
        self.forcing_ghg_2100 = .30
        self.temp_lower_2000 = .0068
        self.temp_atmosphere_2000 = .7307
        self.c1 = .220
        self.c2 = 0
        self.c3 = .300
        self.c4 = .050
        self.thermal_transfer = np.array([
            self.c1, self.c2, self.c3, self.c4
        ])
        self.forcing_co2_doubling = 3.8

        # Climate damage parameters, calibrated for quadratic at 2.5 C for 2105
        self.a1 = 0
        self.damages_coefficient = 0.0028388

        ## Abatement cost
        self.backstop_2005 = 1.17
        self.miu_2005 = .005

        ## Participation
        self.participation_2005 = 1.
        self.participation_2015 = 1.
        self.participation_2205 = 1.
        self.participation_decline = 0.

        self.tmax = 60
        self.t0 = np.arange(self.tmax)
        self.t1 = self.t0 + 1
        self.scc_horizon = self.tmax - 1

        # Variables for initiating pandas array
        backstop_growth = np.zeros(self.tmax)
        carbon_intensity = np.empty(self.tmax)
        carbon_intensity[:] = self.intensity_2005
        intensity_decline = np.zeros(self.tmax)
        intensity_decline[:] = self.intensity_decline_rate
        productivity = np.empty(self.tmax)
        productivity[:] = self.productivity
        capital = np.empty(self.tmax)
        capital[:] = self.capital_2005
        output = np.empty(self.tmax)
        output[:] = self.output_2005
        mass_atmosphere = np.empty(self.tmax)
        mass_atmosphere[:] = self.mass_atmosphere_2005
        mass_upper = np.empty(self.tmax)
        mass_upper[:] = self.mass_upper_2005
        mass_lower = np.empty(self.tmax)
        mass_lower[:] = self.mass_lower_2005
        temp_atmosphere = np.empty(self.tmax)
        temp_atmosphere[:] = self.temp_atmosphere_2000
        temp_lower = np.empty(self.tmax)
        temp_lower[:] = self.temp_lower_2000
        investment = np.empty(self.tmax)
        investment[:] = self.savings * self.output_2005
        population = np.empty(self.tmax)
        population[:] = self.population_2005
        miu = np.empty(self.tmax)
        miu[:] = self.miu_2005

        data = pd.DataFrame({
            'miu': miu,
            'carbon_intensity': carbon_intensity,
            'intensity_decline': intensity_decline,
            'productivity': productivity,
            'backstop_growth': backstop_growth,
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
            'damages': np.zeros(self.tmax),
            'abatement': np.zeros(self.tmax),
            'consumption': np.zeros(self.tmax),
            'consumption_pc': np.zeros(self.tmax),
            'utility': np.zeros(self.tmax),
            'utility_discounted': np.zeros(self.tmax),
            'scc': np.ones(self.tmax),
            'consumption_discount': np.ones(self.tmax),
            'tax_rate': np.zeros(self.tmax),
            'backstop': np.zeros(self.tmax),
            'population': population,
            'population_growth': np.zeros(self.tmax),
            'output_abate': np.zeros(self.tmax),
        })

        self.data = pd.Panel({
            'vars': data,
            'scc': data,
        })


class Dice2010Params(DiceParams):
    def __init__(self):
        super(Dice2010Params, self).__init__(2010)
        self.dice_year = '2010'
        self.temp_co2_doubling = 3.2
        self.damages_exponent = 2.  # TODO: see equations
        self.productivity_decline = .009  # TODO: Add second parameter?
        self.intensity_decline_rate = .00646
        self.popasym = 8700.
        self.elasmu = 1.5

        ## Population and technology
        self.population_2005 = 6411.
        self.population_growth = .5  # This is called Population adjustment in Dice2010
        self.productivity = .0303220
        self.productivity_growth = .16
        self.output_2005 = 55.34

        ## Emissions
        self.intensity_2005 = .14452
        self.intensity_growth = .158

        ## Carbon Cycle
        _b11, _b12, _b13 = .88, .12, 0
        _b21, _b22, _b23 = .04704, .94796, .005
        _b31, _b32, _b33 = 0, .00075, .99925
        self.carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self.mass_atmosphere_2005 = 787.
        self.mass_upper_2005 = 1600.
        self.mass_lower_2005 = 10100.

        ## Climate model
        self.forcing_ghg_2000 = .83
        self.temp_atmosphere_2000 = .83
        self.temp_atmosphere_2010 = .98
        self.thermal_transfer[0] = .208
        self.thermal_transfer[2] = .310

        # self.damages_coefficient = .00204625800317896

        ## Abatement cost
        self.backstop_2005 = 1.26

        self.data.vars.intensity_decline[0] = .158
        self.data.scc.intensity_decline[0] = .158
        self.data.vars.population[0] = self.population_2005
        self.data.scc.population[0] = self.population_2005
        self.data.vars.temp_atmosphere[0] = self.temp_atmosphere_2000
        self.data.vars.temp_atmosphere[1] = self.temp_atmosphere_2010
        self.data.scc.temp_atmosphere[0] = self.temp_atmosphere_2000
        self.data.scc.temp_atmosphere[1] = self.temp_atmosphere_2010
        self.data.vars.carbon_intensity[0] = self.intensity_2005
        self.data.scc.carbon_intensity[0] = self.intensity_2005
        self.data.vars.productivity[0] = self.productivity
        self.data.scc.productivity[0] = self.productivity
        self.data.vars.output[0] = self.output_2005
        self.data.scc.output[0] = self.output_2005
        self.data.vars.mass_atmosphere[0] = self.mass_atmosphere_2005
        self.data.scc.mass_atmosphere[0] = self.mass_atmosphere_2005
        self.data.vars.mass_upper[0] = self.mass_upper_2005
        self.data.scc.mass_upper[0] = self.mass_upper_2005
        self.data.vars.mass_lower[0] = self.mass_lower_2005
        self.data.scc.mass_lower[0] = self.mass_lower_2005