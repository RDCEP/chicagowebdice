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
        self.damages_model = 'dice_damages'
        self.prod_frac = .05
        self.elasmu = 2.
        self.prstp = .015
        self._treaty = False
        self._optimize = False
        self._eps = 1e-4
        self._carbon_tax = False
        self.e2050 = 100.
        self.e2100 = 100.
        self.e2150 = 100.
        self.p2050 = 100.
        self.p2100 = 100.
        self.p2150 = 100.
        self._pmax = 100.
        self.c2050 = 0.
        self.c2100 = 0.
        self.c2150 = 0.
        self._cmax = 500.
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
        self._emissions_deforest_2005 = 1.1 #11.0

        ## Carbon Cycle
        self._mass_atmosphere_2005 = 808.9
        self._mass_upper_2005 = 1255.
        self._mass_lower_2005 = 18365.
        self._mass_preindustrial = 278. * 2.13

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


        population_growth_rate = (
            (np.exp(self._population_growth * self._t0) - 1) /
            (np.exp(self._population_growth * self._t0))
        )

        # Variables for initiating pandas array
        backstop_growth = np.zeros(self._tmax)
        carbon_intensity = np.empty(self._tmax)
        carbon_intensity[:] = self._intensity_2005
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
        miu = np.empty(self._tmax)
        miu[:] = self._miu_2005
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
            'population': np.zeros(self._tmax),
            'output_abate': np.zeros(self._tmax),
        })
        self._data = pd.Panel({
            'vars': data,
            'deriv': data,
            'scc': data,
        })
        self._derivative = pd.DataFrame({
            'fprime': np.empty(self._tmax),
        })
        self._hessian = pd.Series(np.empty(self._tmax))