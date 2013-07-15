from params import DiceParams
import numpy as np

class Dice2010Params(DiceParams):
    def __init__(self):
        super(Dice2010Params, self).__init__()
        dice_version = '2010'
        self.temp_co2_doubling = 3.2
        self.damages_exponent = 2.  # TODO: see equations
        self.productivity_decline = .009  # TODO: Add second parameter?
        self.intensity_decline_rate = .00646
        self.popasym = 8700.
        self.carbon_model = 'dice_%s' % dice_version
        self.consumption_model = 'dice_%s' % dice_version
        self.damages_model = 'dice_%s' % dice_version
        self.emissions_model = 'dice_%s' % dice_version
        self.productivity_model = 'dice_%s' % dice_version
        self.temperature_model = 'dice_%s' % dice_version
        self.utility_model = 'dice_%s' % dice_version
        self.elasmu = 1.5
        ## Population and technology
        self._population_2005 = 6411.
        self._population_growth = .485  # This is called Population adjustment in Dice2010
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
        self._mass_atmosphere_2005 = 829.
        self._mass_upper_2005 = 1600.
        self._mass_lower_2005 = 10100.

        ## Climate model
        self._forcing_ghg_2000 = .083
        self._temp_atmosphere_2000 = .83
        self._temp_atmosphere_2010 = .98

        self._damages_coefficient = .00204625800317896

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