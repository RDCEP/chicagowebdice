from __future__ import division
import numpy as np


class DiceDataMatrix(np.ndarray):
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        obj.abatement = input_array[0]
        obj.backstop = input_array[1]
        obj.backstop_growth = input_array[2]
        obj.capital = input_array[3]
        obj.carbon_emitted = input_array[4]
        obj.carbon_intensity = input_array[5]
        obj.consumption = input_array[6]
        obj.consumption_discount = input_array[7]
        obj.consumption_pc = input_array[8]
        obj.damages = input_array[9]
        obj.emissions_ind = input_array[10]
        obj.emissions_total = input_array[11]
        obj.forcing = input_array[12]
        obj.gross_output = input_array[13]
        obj.intensity_decline = input_array[14]
        obj.investment = input_array[15]
        obj.mass_atmosphere = input_array[16]
        obj.mass_upper = input_array[17]
        obj.mass_lower = input_array[18]
        obj.miu = input_array[19]
        obj.output = input_array[20]
        obj.output_abate = input_array[21]
        obj.participation = input_array[22]
        obj.population = input_array[23]
        obj.population_growth = input_array[24]
        obj.productivity = input_array[25]
        obj.scc = input_array[26]
        obj.tax_rate = input_array[27]
        obj.temp_atmosphere = input_array[28]
        obj.temp_lower = input_array[29]
        obj.utility = input_array[30]
        obj.utility_discounted = input_array[31]
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.abatement = getattr(obj, 'abatement', None)
        self.backstop = getattr(obj, 'backstop', None)
        self.backstop_growth = getattr(obj, 'backstop_growth', None)
        self.capital = getattr(obj, 'capital', None)
        self.carbon_emitted = getattr(obj, 'carbon_emitted', None)
        self.carbon_intensity = getattr(obj, 'carbon_intensity', None)
        self.consumption = getattr(obj, 'consumption', None)
        self.consumption_discount = getattr(obj, 'consumption_discount', None)
        self.consumption_pc = getattr(obj, 'consumption_pc', None)
        self.damages = getattr(obj, 'damages', None)
        self.emissions_ind = getattr(obj, 'emissions_ind', None)
        self.emissions_total = getattr(obj, 'emissions_total', None)
        self.forcing = getattr(obj, 'forcing', None)
        self.gross_output = getattr(obj, 'gross_output', None)
        self.intensity_decline = getattr(obj, 'intensity_decline', None)
        self.investment = getattr(obj, 'investment', None)
        self.mass_atmosphere = getattr(obj, 'mass_atmosphere', None)
        self.mass_upper = getattr(obj, 'mass_upper', None)
        self.mass_lower = getattr(obj, 'mass_lower', None)
        self.miu = getattr(obj, 'miu', None)
        self.output = getattr(obj, 'output', None)
        self.output_abate = getattr(obj, 'output_abate', None)
        self.participation = getattr(obj, 'participation', None)
        self.population = getattr(obj, 'population', None)
        self.population_growth = getattr(obj, 'population_growth', None)
        self.productivity = getattr(obj, 'productivity', None)
        self.scc = getattr(obj, 'scc', None)
        self.tax_rate = getattr(obj, 'tax_rate', None)
        self.temp_atmosphere = getattr(obj, 'temp_atmosphere', None)
        self.temp_lower = getattr(obj, 'temp_lower', None)
        self.utility = getattr(obj, 'utility', None)
        self.utility_discounted = getattr(obj, 'utility_discounted', None)

    def __array_wrap__(self, out_arr, context=None):
        return np.ndarray.__array_wrap__(self, out_arr, context)


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
        self.population_2005 = 6.514
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
        self.c3 = .310
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

        # Variables for initiating DiceDataMatrix
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

        self.vars = DiceDataMatrix(np.array([
            np.zeros(self.tmax),                # abatement
            np.zeros(self.tmax),                # backstop
            backstop_growth,                    # backstop_growth
            capital,                            # capital
            np.zeros(self.tmax),                # carbon_emitted
            carbon_intensity,                   # carbon_intensity
            np.zeros(self.tmax),                # consumption
            np.ones(self.tmax),                 # consumption_discount
            np.zeros(self.tmax),                # consumption_pc
            np.zeros(self.tmax),                # damages
            np.zeros(self.tmax),                # emissions_ind
            np.zeros(self.tmax),                # emissions_total
            np.zeros(self.tmax),                # forcing
            np.zeros(self.tmax),                # gross_output
            intensity_decline,                  # intensity_decline
            investment,                         # investment
            mass_atmosphere,                    # mass_atmosphere
            mass_upper,                         # mass_upper
            mass_lower,                         # mass_lower
            miu,                                # miu
            output,                             # output
            np.zeros(self.tmax),                # output_abate
            np.zeros(self.tmax),                # participation
            population,                         # population
            np.zeros(self.tmax),                # population_growth
            productivity,                       # productivity
            np.ones(self.tmax),                 # scc
            np.zeros(self.tmax),                # tax_rate
            temp_atmosphere,                    # temp_atmosphere
            temp_lower,                         # temp_lower
            np.zeros(self.tmax),                # utility
            np.zeros(self.tmax),                # utility_discounted
        ]))

        self.scc = DiceDataMatrix(np.zeros((32, 60)))


class Dice2010Params(DiceParams):
    def __init__(self):
        super(Dice2010Params, self).__init__(2010)
        self.dice_year = '2010'
        self.temp_co2_doubling = 3.2
        self.damages_exponent = 2.
        self.productivity_decline = .009
        self.intensity_decline_rate = .00646
        self.popasym = 8700.
        self.elasmu = 1.5

        ## Population and technology
        self.population_2005 = 6.411
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

        self.vars.intensity_decline[0] = .158
        self.vars.population[0] = self.population_2005
        self.vars.temp_atmosphere[0] = self.temp_atmosphere_2000
        self.vars.temp_atmosphere[1] = self.temp_atmosphere_2010
        self.vars.carbon_intensity[0] = self.intensity_2005
        self.vars.productivity[0] = self.productivity
        self.vars.output[0] = self.output_2005
        self.vars.mass_atmosphere[0] = self.mass_atmosphere_2005
        self.vars.mass_upper[0] = self.mass_upper_2005
        self.vars.mass_lower[0] = self.mass_lower_2005