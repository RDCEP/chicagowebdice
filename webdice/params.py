import numpy as np
import pandas as pd


class Dice2007Params(object):
    def __init__(self):
        self.temp_co2_doubling = 3.
        self.damages_exponent = 2.
        self.productivity_decline = .1
        self.intensity_decline_rate = .3
        self.abatement_exponent = 2.8
        self.backstop_decline = .05
        self.backstop_ratio = 2.
        self.popasym = 8600.
        self.depreciation = .1
        self.savings = .2
        self.fosslim = 6000.
        self.carbon_model = 'dice_carbon'
        self.damages_model = 'dice_output'
        self.prod_frac = .05
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
        self._population_2005 = 6514.
        self._population_growth = .35
        self._productivity = .02722
        self._productivity_growth = .092
        self._output_elasticty = .300
        self._output_2005 = 61.1
        self._output_2005 = 55.667
        self._capital_2005 = 137.

        ## Emissions
        self._intensity_2005 = .13418
        self._intensity_growth = -.0730
        self._intensity_quadratic = .000
        self._emissions_deforest_2005 = 11.0

        ## Carbon Cycle
        self._mass_atmosphere_2005 = 808.9
        self._mass_upper_2005 = 1255.
        self._mass_lower_2005 = 18365.
        self._mass_preindustrial = 278. * 2.13
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
        self.carbon_matrix = np.array([
            self.b11, self.b12, self.b13, self.b21, self.b22, self.b23,
            self.b31, self.b32, self.b33
        ]).reshape(3, 3)

        ## Climate model
        self._forcing_ghg_2000 = -.06
        self._forcing_ghg_2100 = .30
        self._temp_lower_2000 = .0068
        self._temp_atmosphere_2000 = .7307
        self.c1 = .220
        self.c2 = 0
        self.c3 = .300
        self.c4 = .050
        self.thermal_transfer = np.array([self.c1, self.c2, self.c3, self.c4])
        self._forcing_co2_doubling = 3.8
        # Climate damage parameters, calibrated for quadratic at 2.5 C for 2105
        self.a1 = 0
        self._damages_coefficient = 0.0028388

        ## Abatement cost
        self._backstop_2005 = 1.17
        self.miu_upper = 1.  # Upper limit on control rate
        self.miu_2005 = .005

        ## Participation
        self._participation_2005 = 1.
        self._participation_2015 = 1.
        self._participation_2205 = 1.
        self._participation_decline = 0.

        self.tmax = 60  # Time periods, in decades (60 * 10 = 600 years)
        self.t0 = np.arange(float(self.tmax))
        self.t1 = self.t0 + 1

        ## Scaling and inessential parameters
        self.scale1 = 194.  # Scaling coefficient in the objective function
        self.scale2 = 381800.  # Scaling coefficient in the objective function

        # Variables for initiating pandas array
        backstop_growth = np.zeros(self.tmax)
        carbon_intensity = np.empty(self.tmax)
        carbon_intensity[:] = self._intensity_2005
        productivity = np.empty(self.tmax)
        productivity[:] = self._productivity
        capital = np.empty(self.tmax)
        capital[:] = self._capital_2005
        output = np.empty(self.tmax)
        output[:] = self._output_2005
        mass_atmosphere = np.empty(self.tmax)
        mass_atmosphere[:] = self._mass_atmosphere_2005
        mass_upper = np.empty(self.tmax)
        mass_upper[:] = self._mass_upper_2005
        mass_lower = np.empty(self.tmax)
        mass_lower[:] = self._mass_lower_2005
        temp_atmosphere = np.empty(self.tmax)
        temp_atmosphere[:] = self._temp_atmosphere_2000
        temp_lower = np.empty(self.tmax)
        temp_lower[:] = self._temp_lower_2000
        investment = np.empty(self.tmax)
        investment[:] = self.savings * self._output_2005
        miu = np.empty(self.tmax)
        miu[:] = self.miu_2005
        data = pd.DataFrame({
            'miu': miu,
            'carbon_intensity': carbon_intensity,
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
            'participation_markup': np.zeros(self.tmax),
            'damage': np.zeros(self.tmax),
            'abatement': np.zeros(self.tmax),
            'consumption': np.zeros(self.tmax),
            'consumption_pc': np.zeros(self.tmax),
            'utility': np.zeros(self.tmax),
            'utility_d': np.zeros(self.tmax),
            'pref_fac': np.ones(self.tmax),
            'scc': np.ones(self.tmax),
            'consumption_discount': np.ones(self.tmax),
            'tax_rate': np.zeros(self.tmax),
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