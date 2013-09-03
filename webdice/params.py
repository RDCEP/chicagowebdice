from __future__ import division
import numpy as np
import pandas as pd


class DiceParams(object):
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
        self.savings = .2
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
        self._treaty = False
        self._optimize = False
        self._eps = 1e-4
        self._carbon_tax = False
        self.e2050 = 1.
        self.e2100 = 1.
        self.e2150 = 1.
        self.p2050 = 1.
        self.p2100 = 1.
        self.p2150 = 1.
        self._pmax = 1.
        self.c2050 = 0.
        self.c2100 = 0.
        self.c2150 = 0.
        self._cmax = 500.
        ## Population and technology
        self._population_2005 = 6514.
        self._population_growth = .35
        self._productivity = .02722
        self._productivity_growth = .092
        self._output_elasticity = .300
        self._output_2005 = 61.1
        self._output_2005 = 55.667
        self._capital_2005 = 137.

        ## Emissions
        self._intensity_2005 = .13418
        self._intensity_growth = -.0730
        self._intensity_quadratic = .000
        self._emissions_deforest_2005 = 1.1 #11.0

        ## Carbon Cycle
        _b11, _b12, _b13 = .810712, .189288, 0
        _b21, _b22, _b23 = .097213, .852787, .05
        _b31, _b32, _b33 = 0, .003119, .996881
        self._carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self._mass_atmosphere_2005 = 808.9
        self._mass_upper_2005 = 1255.
        self._mass_lower_2005 = 18365.
        self._mass_preindustrial = 592.14  # 278. * 2.13

        ## Climate model
        self._forcing_ghg_2000 = -.06
        self._forcing_ghg_2100 = .30
        self._temp_lower_2000 = .0068
        self._temp_atmosphere_2000 = .7307
        self._c1 = .220
        self._c2 = 0
        self._c3 = .300
        self._c4 = .050
        self.thermal_transfer = np.array([
            self._c1, self._c2, self._c3, self._c4
        ])
        self._forcing_co2_doubling = 3.8
        # Climate damage parameters, calibrated for quadratic at 2.5 C for 2105
        self._a1 = 0
        self._damages_coefficient = 0.0028388

        ## Abatement cost
        self._backstop_2005 = 1.17
        self._miu_upper = 1.  # Upper limit on control rate
        self._miu_2005 = .005

        ## Participation
        self._participation_2005 = 1.
        self._participation_2015 = 1.
        self._participation_2205 = 1.
        self._participation_decline = 0.

        self._tmax = 60  # Time periods, in decades (60 * 10 = 600 years)
        self._t0 = np.arange(float(self._tmax))
        self._t1 = self._t0 + 1

        ## Scaling and inessential parameters
        self._scale1 = 194.  # Scaling coefficient in the objective function
        self._scale2 = 381800.  # Scaling coefficient in the objective function

        # Variables for initiating pandas array
        backstop_growth = np.zeros(self._tmax)
        carbon_intensity = np.empty(self._tmax)
        carbon_intensity[:] = self._intensity_2005
        intensity_decline = np.zeros(self._tmax)
        intensity_decline[:] = self.intensity_decline_rate
        productivity = np.empty(self._tmax)
        productivity[:] = self._productivity
        capital = np.empty(self._tmax)
        capital[:] = self._capital_2005
        output = np.empty(self._tmax)
        output[:] = self._output_2005
        mass_atmosphere = np.empty(self._tmax)
        mass_atmosphere[:] = self._mass_atmosphere_2005
        mass_upper = np.empty(self._tmax)
        mass_upper[:] = self._mass_upper_2005
        mass_lower = np.empty(self._tmax)
        mass_lower[:] = self._mass_lower_2005
        temp_atmosphere = np.empty(self._tmax)
        temp_atmosphere[:] = self._temp_atmosphere_2000
        temp_lower = np.empty(self._tmax)
        temp_lower[:] = self._temp_lower_2000
        investment = np.empty(self._tmax)
        investment[:] = self.savings * self._output_2005
        population = np.empty(self._tmax)
        population[:] = self._population_2005
        miu = np.empty(self._tmax)
        miu[:] = self._miu_2005
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
            'gross_output': np.zeros(self._tmax),
            'forcing': np.zeros(self._tmax),
            'emissions_ind': np.zeros(self._tmax),
            'emissions_total': np.zeros(self._tmax),
            'carbon_emitted': np.zeros(self._tmax),
            'participation': np.zeros(self._tmax),
            'damages': np.zeros(self._tmax),
            'abatement': np.zeros(self._tmax),
            'consumption': np.zeros(self._tmax),
            'consumption_pc': np.zeros(self._tmax),
            'utility': np.zeros(self._tmax),
            'utility_discounted': np.zeros(self._tmax),
            'scc': np.ones(self._tmax),
            'consumption_discount': np.ones(self._tmax),
            'tax_rate': np.zeros(self._tmax),
            'backstop': np.zeros(self._tmax),
            'population': population,
            'population_growth': np.zeros(self._tmax),
            'output_abate': np.zeros(self._tmax),
        })
        self._data = pd.Panel({
            'vars': data,
            'deriv': data,
            'scc': data,
        })
        d_V = {}
        for i in xrange(self._tmax):
            d_V[i] = data
        self.deriv_work = pd.Panel(d_V)
        self._derivative = pd.DataFrame({
            'fprime': np.empty(self._tmax),
        })
        # self._hessian = pd.Series(np.empty(self._tmax))


class Dice2010Params(DiceParams):
    def __init__(self):
        super(Dice2010Params, self).__init__(2010)
        self.temp_co2_doubling = 3.2
        self.damages_exponent = 2.  # TODO: see equations
        self.productivity_decline = .009  # TODO: Add second parameter?
        self.intensity_decline_rate = .00646
        self.popasym = 8700.
        self.elasmu = 1.5
        ## Population and technology
        self._population_2005 = 6411.
        self._population_growth = .5  # This is called Population adjustment in Dice2010
        self._productivity = .0303220
        self._productivity_growth = .16
        self._output_2005 = 55.34
        ## Emissions
        self._intensity_2005 = .14452
        self._intensity_growth = .158
        ## Carbon Cycle
        _b11, _b12, _b13 = .88, .12, 0
        _b21, _b22, _b23 = .04704, .94796, .005
        _b31, _b32, _b33 = 0, .00075, .99925
        self._carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        # self._mass_atmosphere_2005 = (787 + 829) / 2
        self._mass_atmosphere_2005 = 787.
        self._mass_upper_2005 = 1600.
        self._mass_lower_2005 = 10100.

        ## Climate model
        self._forcing_ghg_2000 = .83
        self._temp_atmosphere_2000 = .83
        self._temp_atmosphere_2010 = .98
        self.thermal_transfer[0] = .208
        self.thermal_transfer[2] = .310

        # self._damages_coefficient = .00204625800317896

        ## Abatement cost
        self._backstop_2005 = 1.26

        self._data.vars.intensity_decline[0] = .158
        self._data.scc.intensity_decline[0] = .158
        self._data.vars.population[0] = self._population_2005
        self._data.scc.population[0] = self._population_2005
        self._data.vars.temp_atmosphere[0] = self._temp_atmosphere_2000
        self._data.vars.temp_atmosphere[1] = self._temp_atmosphere_2010
        self._data.scc.temp_atmosphere[0] = self._temp_atmosphere_2000
        self._data.scc.temp_atmosphere[1] = self._temp_atmosphere_2010
        self._data.vars.carbon_intensity[0] = self._intensity_2005
        self._data.scc.carbon_intensity[0] = self._intensity_2005
        self._data.vars.productivity[0] = self._productivity
        self._data.scc.productivity[0] = self._productivity
        self._data.vars.output[0] = self._output_2005
        self._data.scc.output[0] = self._output_2005
        self._data.vars.mass_atmosphere[0] = self._mass_atmosphere_2005
        self._data.scc.mass_atmosphere[0] = self._mass_atmosphere_2005
        self._data.vars.mass_upper[0] = self._mass_upper_2005
        self._data.scc.mass_upper[0] = self._mass_upper_2005
        self._data.vars.mass_lower[0] = self._mass_lower_2005
        self._data.scc.mass_lower[0] = self._mass_lower_2005