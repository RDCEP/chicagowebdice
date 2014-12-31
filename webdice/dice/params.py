from __future__ import division
import numpy as np


class DiceDataMatrix(np.ndarray):
    """DiceDataMatrix

    Subclasses nd.array to provide attribute-like access to model
    variables within the numpy array.
    """
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
    """User-defined parameters for the model.

    This is a mixin for the parameter objects below which are used for
    DICE2007, 2010, and 2013. Values in this mixin are for DICE2007.
    """
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


class Dice2007Params(DiceUserParams):
    """Parameters for emulating DICE2007."""
    def __init__(self, model=2007):
        DiceUserParams.__init__(self, model=model)
        self.dice_version = str(model)
        self.treaty = False
        self.carbon_tax = False
        self.pmax = 1.
        self.cmax = 500.

        ## Population and technology
        self.population_init = 6514.
        self.population_growth = .35
        self.productivity = .02722
        self.productivity_growth_init = .092
        self.output_elasticity = .300
        self.output_init = 61.1
        self.output_init = 55.667
        self.capital_init = 137.

        ## Emissions
        self.intensity_init = .13418
        self.intensity_growth = -.0730
        self.intensity_quadratic = .000
        self.emissions_deforest_init = 1.1

        ## Carbon Cycle
        _b11, _b12, _b13 = .810712, .189288, 0
        _b21, _b22, _b23 = .097213, .852787, .05
        _b31, _b32, _b33 = 0, .003119, .996881
        self.carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self.mass_atmosphere_init = 808.9
        self.mass_upper_init = 1255.
        self.mass_lower_init = 18365.
        self.mass_preindustrial = 592.14

        ## Climate model
        self.forcing_ghg_init = -.06
        self.forcing_ghg_future = .30
        self.temp_lower_init = .0068
        self.temp_atmosphere_init = .7307
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
        self.backstop_init = 1.17
        self.miu_init = .005

        self.tmax = 60
        self.t0 = np.arange(self.tmax)
        self.t1 = self.t0 + 1
        self.ts = 10.
        self.start_year = 2005
        self.scc_horizon = self.tmax - 1

        # Variables for initiating DiceDataMatrix
        backstop_growth = np.zeros(self.tmax)
        carbon_intensity = np.empty(self.tmax)
        carbon_intensity[:] = self.intensity_init
        intensity_decline = np.zeros(self.tmax)
        intensity_decline[:] = self.intensity_decline_rate
        productivity = np.empty(self.tmax)
        productivity[:] = self.productivity
        capital = np.empty(self.tmax)
        capital[:] = self.capital_init
        output = np.empty(self.tmax)
        output[:] = self.output_init
        mass_atmosphere = np.empty(self.tmax)
        mass_atmosphere[:] = self.mass_atmosphere_init
        mass_upper = np.empty(self.tmax)
        mass_upper[:] = self.mass_upper_init
        mass_lower = np.empty(self.tmax)
        mass_lower[:] = self.mass_lower_init
        temp_atmosphere = np.empty(self.tmax)
        temp_atmosphere[:] = self.temp_atmosphere_init
        temp_lower = np.empty(self.tmax)
        temp_lower[:] = self.temp_lower_init
        investment = np.empty(self.tmax)
        investment[:] = self.savings * self.output_init
        population = np.empty(self.tmax)
        population[:] = self.population_init
        miu = np.empty(self.tmax)
        miu[:] = self.miu_init

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


class Dice2010Params(Dice2007Params):
    """Parameters for emulating DICE2010."""
    def __init__(self, model=2010):
        super(Dice2010Params, self).__init__(model=model)
        self.dice_year = str(model)
        self.temp_co2_doubling = 3.2
        self.damages_exponent = 2.  # TODO: see equations
        self.productivity_decline = .009  # TODO: Add second parameter?
        self.intensity_decline_rate = .00646
        self.popasym = 8700.
        self.elasmu = 1.5

        ## Population and technology
        self.population_init = 6411.
        self.population_growth = .5  # This is called Population adjustment in Dice2010
        self.productivity = .0303220
        self.productivity_growth_init = .16
        self.output_init = 55.34

        ## Emissions
        self.intensity_init = .14452
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
        self.mass_atmosphere_init = 787.
        self.mass_upper_init = 1600.
        self.mass_lower_init = 10100.

        ## Climate model
        self.forcing_ghg_init = .83
        self.temp_atmosphere_init = .83
        self.thermal_transfer[0] = .208
        self.thermal_transfer[2] = .310

        # self.damages_coefficient = .00204625800317896

        ## Abatement cost
        self.backstop_init = 1.26

        self.vars.intensity_decline[0] = .158
        self.vars.population[0] = self.population_init
        self.vars.temp_atmosphere[0] = self.temp_atmosphere_init
        self.vars.carbon_intensity[0] = self.intensity_init
        self.vars.productivity[0] = self.productivity
        self.vars.output[0] = self.output_init
        self.vars.mass_atmosphere[0] = self.mass_atmosphere_init
        self.vars.mass_upper[0] = self.mass_upper_init
        self.vars.mass_lower[0] = self.mass_lower_init


class Dice2013Params(Dice2007Params):
    """Parameters for emulating DICE2013.

    Note that DICE2013 runs on 5-year timesteps rather than 10-year.
    As such, tmax is double that of DICE2007 and DICE2010 Params.
    """
    def __init__(self, model=2013):
        super(Dice2013Params, self).__init__(model=model)
        self.dice_year = str(model)

        self.tmax *= 2
        self.t0 = np.arange(self.tmax)
        self.t1 = self.t0 + 1
        self.ts = 5.
        self.start_year = 2010
        self.scc_horizon = self.tmax - 1

        self.intensity_init = .489 * 12 / 44
        self.intensity_growth = -.01
        self.intensity_decline_rate = .001

        self.emissions_deforest_init = 1.54
        #self.emissions_deforest_init = 3.3 #GAMS
        self.miu_init = .039

        self.elasmu = 1.45

        self.population_init = 6838.
        self.population_growth = .134
        self.popasym = 10500

        self.output_init = 63.69
        self.capital_init = 135.
        self.savings = .25

        self.productivity = 3.8
        self.productivity_growth_init = .079
        self.productivity_decline = .006

        self.backstop_init = 1.26

        _b13 = 0
        _b31 = 0
        _b12 = .088
        _b23 = .0025
        _b11 = 1 - _b12
        _b21 = _b12 * 588. / 1350.
        _b22 = 1 - _b21 - _b23
        _b32 = _b23 * 1350. / 10000.
        _b33 = 1 - _b32
        self.carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self.mass_atmosphere_init = 830.4
        self.mass_upper_init = 1527.
        self.mass_lower_init = 10010.
        self.mass_preindustrial = 592.14

        # self.temp_co2_doubling = 2.9  # GAMS
        # self.forcing_ghg_init = .25  # GAMS
        # self.forcing_ghg_future = .7  # GAMS
        self.forcing_ghg_init = -.06  # XLS
        self.forcing_ghg_future = .62  # XLS
        self.temp_co2_doubling = 3.2  # XLS
        self.temp_atmosphere_init = .83

        self.c10 = .098  # GAMS
        self.c1beta = .01243  # GAMS
        # self.c1 = .098  # GAMS
        # self.c3 = .088  # GAMS
        # self.c4 = .025  # GAMS
        self.c1 = .104  # XLS
        self.c3 = .155  # XLS
        self.c4 = .025  # XLS
        self.thermal_transfer = np.array([
            self.c1, self.c2, self.c3, self.c4
        ])

        self.a1 = 0
        self.damages_coefficient = 0.002131
        self.damages_multiplier = 1.25
        self.catastrophic_rate = .00644
        self.catastrophic_threshold = 4.
        self.catastrophic_exponent = 3.
        self.catastrophic_gate = 0

        backstop_growth = np.zeros(self.tmax)
        carbon_intensity = np.empty(self.tmax)
        carbon_intensity[:] = self.intensity_init
        intensity_decline = np.zeros(self.tmax)
        intensity_decline[:] = self.intensity_decline_rate
        productivity = np.empty(self.tmax)
        productivity[:] = self.productivity
        capital = np.empty(self.tmax)
        capital[:] = self.capital_init
        output = np.empty(self.tmax)
        output[:] = self.output_init
        mass_atmosphere = np.empty(self.tmax)
        mass_atmosphere[:] = self.mass_atmosphere_init
        mass_upper = np.empty(self.tmax)
        mass_upper[:] = self.mass_upper_init
        mass_lower = np.empty(self.tmax)
        mass_lower[:] = self.mass_lower_init
        temp_atmosphere = np.empty(self.tmax)
        temp_atmosphere[:] = self.temp_atmosphere_init
        temp_lower = np.empty(self.tmax)
        temp_lower[:] = self.temp_lower_init
        investment = np.empty(self.tmax)
        investment[:] = self.savings * self.output_init
        population = np.empty(self.tmax)
        population[:] = self.population_init
        miu = np.empty(self.tmax)
        miu[:] = self.miu_init

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

        self.scc = DiceDataMatrix(np.zeros((32, self.tmax)))
